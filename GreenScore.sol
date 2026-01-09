// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Import các thư viện chuẩn từ OpenZeppelin
// Giúp tạo NFT và quản lý quyền Admin an toàn
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title GreenScore Registry
 * @dev Smart Contract lưu trữ điểm ESG, Hash báo cáo và cấp NFT chứng nhận.
 */
contract GreenScore is ERC721URIStorage, Ownable {
    uint256 private _tokenIds; // Bộ đếm ID cho NFT

    // --- 1. DATA STRUCTURES (Cấu trúc dữ liệu) ---

    // Struct lưu lịch sử mỗi lần chấm điểm (Bất biến)
    struct ESGReport {
        string ipfsHash;    // Link file JSON chi tiết trên IPFS (Chứa E1-E5, lời khuyên...)
        uint256 totalScore; // Điểm tổng kết (0-100)
        uint256 eScore;     // Điểm Môi trường
        uint256 sScore;     // Điểm Xã hội
        uint256 gScore;     // Điểm Quản trị
        string rank;        // Xếp hạng: GOLD, SILVER, BRONZE, UNRANKED
        bool isPenalized;   // True nếu bị phạt (thiếu dữ liệu trọng yếu)
        uint256 timestamp;  // Thời điểm ghi nhận
        address auditor;    // Ví của AI Agent/Người chấm
    }

    // Struct quản lý hồ sơ công ty (Trạng thái hiện tại)
    struct Company {
        string name;            // Tên công ty (VD: Vinamilk)
        bool isRegistered;      // Đã đăng ký hay chưa
        uint256 currentScore;   // Điểm số mới nhất
        string currentRank;     // Hạng hiện tại
        uint256 nftId;          // ID của NFT chứng nhận (nếu có)
    }

    // --- 2. STATE VARIABLES (Bộ nhớ lưu trữ) ---

    // Tra cứu thông tin công ty từ địa chỉ ví
    mapping(address => Company) public companies;
    
    // Lưu danh sách lịch sử báo cáo của một công ty
    mapping(address => ESGReport[]) public companyReports;
    
    // Danh sách các Auditor (AI Agent) được quyền ghi điểm
    mapping(address => bool) public auditors;

    // --- 3. EVENTS (Sự kiện cho Frontend) ---

    event CompanyRegistered(address indexed companyAddress, string name);
    
    event ScoreSubmitted(
        address indexed companyAddress, 
        uint256 totalScore, 
        string rank, 
        bool isPenalized, 
        uint256 timestamp
    );

    event NFTMinted(address indexed companyAddress, uint256 tokenId, string rank);

    // --- 4. CONSTRUCTOR & MODIFIERS ---

    constructor() ERC721("GreenScore Certificate", "GSC") Ownable(msg.sender) {
        // Người deploy (Bình) mặc định là Admin và có quyền Auditor để test
        auditors[msg.sender] = true;
    }

    // Modifier chỉ cho phép Auditor (AI Agent) gọi hàm
    modifier onlyAuditor() {
        require(auditors[msg.sender] || msg.sender == owner(), "GreenScore: Access Denied. Caller is not an Auditor.");
        _;
    }

    // --- 5. MAIN FUNCTIONS (Chức năng chính) ---

    /**
     * @dev Hàm B2.1: Đăng ký doanh nghiệp mới
     * @param _name Tên doanh nghiệp
     */
    function registerCompany(string memory _name) external {
        require(!companies[msg.sender].isRegistered, "GreenScore: Company already registered.");
        
        // Khởi tạo hồ sơ công ty
        companies[msg.sender] = Company({
            name: _name,
            isRegistered: true,
            currentScore: 0,
            currentRank: "UNRANKED",
            nftId: 0
        });

        emit CompanyRegistered(msg.sender, _name);
    }

    /**
     * @dev Hàm B2.2: Ghi điểm và Hash báo cáo (Dành cho AI Agent - Hùng)
     * Logic xếp hạng và luật phạt nằm ở đây.
     */
    function submitScore(
        address _companyAddr,       // Ví công ty
        string memory _ipfsHash,    // Hash file chi tiết trên IPFS
        uint256 _totalScore,        // Điểm tổng
        uint256 _eScore,            // Điểm E
        uint256 _sScore,            // Điểm S
        uint256 _gScore,            // Điểm G
        bool _isCriticalMissing,    // True nếu thiếu dữ liệu bắt buộc (Luật phạt)
        string memory _tokenURI     // Link metadata ảnh NFT (nếu được cấp)
    ) external onlyAuditor {
        require(companies[_companyAddr].isRegistered, "GreenScore: Company not registered.");
        require(_totalScore <= 100, "GreenScore: Score must be <= 100.");

        // --- Logic Xếp hạng & Luật phạt (Task B1 Spec) ---
        string memory newRank = "UNRANKED";

        if (_totalScore >= 80 && !_isCriticalMissing) {
            newRank = "GOLD";
        } else if (_totalScore >= 55) {
            newRank = "SILVER";
        } else if (_totalScore >= 35) {
            newRank = "BRONZE";
        } else {
            newRank = "UNRANKED"; // Dưới 35 hoặc bị phạt nặng thì không có hạng
        }

        // --- Lưu trữ vào Blockchain ---
        companyReports[_companyAddr].push(ESGReport({
            ipfsHash: _ipfsHash,
            totalScore: _totalScore,
            eScore: _eScore,
            sScore: _sScore,
            gScore: _gScore,
            rank: newRank,
            isPenalized: _isCriticalMissing,
            timestamp: block.timestamp,
            auditor: msg.sender
        }));

        // Cập nhật trạng thái hiện tại
        companies[_companyAddr].currentScore = _totalScore;
        companies[_companyAddr].currentRank = newRank;

        emit ScoreSubmitted(_companyAddr, _totalScore, newRank, _isCriticalMissing, block.timestamp);

        // --- Tự động cấp NFT nếu đạt chuẩn (Task B4) ---
        // Chỉ cấp nếu đạt hạng Bronze trở lên (Rank khác "UNRANKED")
        if (keccak256(bytes(newRank)) != keccak256(bytes("UNRANKED"))) {
            _mintCertificate(_companyAddr, _tokenURI, newRank);
        }
    }

    /**
     * @dev Hàm nội bộ để Mint NFT
     */
    function _mintCertificate(address _companyAddr, string memory _tokenURI, string memory _rank) internal {
        _tokenIds++;
        uint256 newItemId = _tokenIds;

        _mint(_companyAddr, newItemId);
        _setTokenURI(newItemId, _tokenURI); // Gán hình ảnh chứng chỉ vào NFT

        companies[_companyAddr].nftId = newItemId;
        emit NFTMinted(_companyAddr, newItemId, _rank);
    }

    // --- 6. ADMIN FUNCTIONS ---

    /**
     * @dev Cấp quyền cho AI Agent mới (Backend của Hùng)
     */
    function addAuditor(address _auditor) external onlyOwner {
        auditors[_auditor] = true;
    }

    // --- 7. READ FUNCTIONS (Cho Dashboard - Dung) ---

    /**
     * @dev Lấy báo cáo mới nhất để hiển thị và verify
     */
    function getLatestReport(address _companyAddr) external view returns (ESGReport memory) {
        require(companyReports[_companyAddr].length > 0, "GreenScore: No reports found.");
        uint256 len = companyReports[_companyAddr].length;
        return companyReports[_companyAddr][len - 1];
    }

    /**
     * @dev Lấy số lượng báo cáo lịch sử
     */
    function getHistoryCount(address _companyAddr) external view returns (uint256) {
        return companyReports[_companyAddr].length;
    }
}