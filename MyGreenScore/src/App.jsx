import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, LayoutDashboard, History, FileText, 
  CheckCircle2, Globe, Users, Building2, ArrowRight, 
  Menu, Bell, Search, Download, Wallet, LogIn, ChevronRight,
  Briefcase, Loader2, ArrowLeft
} from 'lucide-react';

// --- MOCK SMART CONTRACT & DATA (Giả lập Blockchain) ---

const initialData = {
  name: "VinFast Auto Ltd.",
  ticker: "VFS",
  score: 0, 
  rank: "Checking...",
  network: "Polygon POS",
  ipfsHash: null,
  isVerified: false,
  metrics: [
    { id: 1, label: "Environment (Môi trường)", value: 0, color: "bg-emerald-500", icon: <Globe size={18} /> },
    { id: 2, label: "Social (Xã hội)", value: 0, color: "bg-blue-500", icon: <Users size={18} /> },
    { id: 3, label: "Governance (Quản trị)", value: 0, color: "bg-purple-500", icon: <Building2 size={18} /> },
  ]
};

const mockSmartContractCall = async () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        totalScore: 78,
        rank: "Silver Plus",
        ipfsHash: "QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco",
        metrics: [82, 68, 85],
        verified: true
      });
    }, 2500); // Giả lập mạng chậm 2.5s
  });
};

export default function App() {
  const [view, setView] = useState('landing'); 
  const [userRole, setUserRole] = useState('guest');
  const [companyData, setCompanyData] = useState(initialData);
  const [isLoadingChain, setIsLoadingChain] = useState(false);

  // Hàm gọi Blockchain
  const fetchBlockchainData = async () => {
    setIsLoadingChain(true);
    try {
      const data = await mockSmartContractCall();
      setCompanyData(prev => ({
        ...prev,
        score: data.totalScore,
        rank: data.rank,
        ipfsHash: data.ipfsHash,
        isVerified: true,
        metrics: [
          { ...prev.metrics[0], value: data.metrics[0] },
          { ...prev.metrics[1], value: data.metrics[1] },
          { ...prev.metrics[2], value: data.metrics[2] },
        ]
      }));
    } catch (error) {
      console.error("Lỗi Smart Contract:", error);
    } finally {
      setIsLoadingChain(false);
    }
  };

  const handleInvestorAccess = () => {
    setUserRole('guest');
    setView('dashboard');
    fetchBlockchainData(); // Tự động check khi khách vào
  };

  const handleBusinessRegister = (formData) => {
    setUserRole('business');
    setCompanyData(prev => ({ ...prev, name: formData.companyName, ticker: formData.taxId }));
    setView('dashboard');
  };

  if (view === 'landing') return <LandingScreen onInvestor={handleInvestorAccess} onBusiness={() => setView('register')} />;
  if (view === 'register') return <RegisterScreen onBack={() => setView('landing')} onSubmit={handleBusinessRegister} />;
  
  return (
    <MainDashboard 
      data={companyData} 
      isLoading={isLoadingChain}
      userRole={userRole} 
      onLogout={() => { setView('landing'); setCompanyData(initialData); }} 
      onRefreshChain={fetchBlockchainData}
    />
  );
}

// --- 1. LANDING SCREEN ---
function LandingScreen({ onInvestor, onBusiness }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 p-6 relative overflow-hidden">
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-[100px]"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-[100px]"></div>
      </div>

      <div className="z-10 w-full max-w-5xl animate-in fade-in zoom-in duration-500">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-3 mb-4">
            <ShieldCheck className="text-emerald-400" size={56} />
            <h1 className="text-6xl font-black text-white tracking-tighter">GreenScore</h1>
          </div>
          <p className="text-slate-400 text-xl max-w-xl mx-auto">Nền tảng minh bạch hóa dữ liệu ESG doanh nghiệp bằng Blockchain & AI.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div onClick={onInvestor} className="group bg-white/5 hover:bg-white/10 border border-white/10 hover:border-emerald-500/50 p-10 rounded-[2.5rem] cursor-pointer transition-all hover:-translate-y-2">
            <div className="w-16 h-16 bg-blue-500/20 rounded-2xl flex items-center justify-center text-blue-400 mb-6 group-hover:scale-110 transition-transform"><Search size={32} /></div>
            <h2 className="text-2xl font-bold text-white mb-2">Tra cứu Hồ sơ</h2>
            <p className="text-slate-400 mb-6 text-sm">Dành cho Nhà đầu tư xác thực điểm số ESG từ Smart Contract.</p>
            <div className="flex items-center text-blue-400 font-bold text-sm">Truy cập ngay <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-2 transition-transform" /></div>
          </div>

          <div onClick={onBusiness} className="group bg-emerald-900/20 hover:bg-emerald-900/30 border border-emerald-500/20 hover:border-emerald-400 p-10 rounded-[2.5rem] cursor-pointer transition-all hover:-translate-y-2">
            <div className="w-16 h-16 bg-emerald-500/20 rounded-2xl flex items-center justify-center text-emerald-400 mb-6 group-hover:scale-110 transition-transform"><Briefcase size={32} /></div>
            <h2 className="text-2xl font-bold text-white mb-2">Đăng ký Doanh nghiệp</h2>
            <p className="text-slate-400 mb-6 text-sm">Nộp báo cáo, nhận đánh giá AI và cấp chứng chỉ Green Passport.</p>
            <div className="flex items-center text-emerald-400 font-bold text-sm">Tạo hồ sơ mới <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-2 transition-transform" /></div>
          </div>
        </div>
      </div>
    </div>
  );
}

// --- 2. REGISTER SCREEN ---
function RegisterScreen({ onBack, onSubmit }) {
  const [formData, setFormData] = useState({ companyName: '', taxId: '', industry: 'SX' });
  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="bg-white p-10 rounded-[2rem] w-full max-w-lg shadow-2xl relative animate-in slide-in-from-right-10 duration-300">
        <button onClick={onBack} className="absolute top-6 left-6 text-slate-400 hover:text-slate-800"><ArrowLeft /></button>
        <h2 className="text-3xl font-black text-slate-800 text-center mb-8">Đăng ký Hồ sơ</h2>
        <div className="space-y-5">
          <div>
            <label className="block text-sm font-bold text-slate-700 mb-2">Tên Doanh nghiệp</label>
            <input type="text" className="w-full bg-slate-50 border border-slate-200 rounded-xl p-4 font-bold text-slate-900 focus:outline-emerald-500" placeholder="Ví dụ: VinFast Auto Ltd." value={formData.companyName} onChange={e => setFormData({...formData, companyName: e.target.value})} />
          </div>
          <div>
            <label className="block text-sm font-bold text-slate-700 mb-2">Mã số thuế / Mã CK</label>
            <input type="text" className="w-full bg-slate-50 border border-slate-200 rounded-xl p-4 font-bold text-slate-900 focus:outline-emerald-500" placeholder="Ví dụ: VFS" value={formData.taxId} onChange={e => setFormData({...formData, taxId: e.target.value})} />
          </div>
          <button onClick={() => onSubmit(formData)} className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-4 rounded-xl shadow-lg mt-4 flex items-center justify-center gap-2">
            <Wallet size={20} /> Kết nối Ví & Hoàn tất
          </button>
        </div>
      </div>
    </div>
  );
}

// --- 3. MAIN DASHBOARD ---
function MainDashboard({ data, isLoading, userRole, onLogout, onRefreshChain }) {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  return (
    <div className="flex min-h-screen bg-slate-50 font-sans text-slate-900 overflow-hidden">
      <aside className={`bg-slate-900 text-white flex flex-col fixed h-full shadow-xl z-50 transition-all duration-300 ${isSidebarOpen ? 'w-64' : 'w-20'}`}>
        <div className="p-6 flex items-center gap-3 border-b border-slate-800 h-20">
          <ShieldCheck className="text-emerald-400 shrink-0" size={32} />
          {isSidebarOpen && <span className="font-bold text-xl tracking-tight">GreenScore</span>}
        </div>
        <nav className="flex-1 p-4 space-y-2 mt-4">
          <SidebarItem icon={<LayoutDashboard size={20} />} label="Tổng quan" isActive={activeTab === 'dashboard'} onClick={() => setActiveTab('dashboard')} isOpen={isSidebarOpen} />
          {userRole === 'business' && <SidebarItem icon={<FileText size={20} />} label="Nộp báo cáo" isActive={activeTab === 'analysis'} onClick={() => setActiveTab('analysis')} isOpen={isSidebarOpen} />}
          <SidebarItem icon={<History size={20} />} label="Lịch sử chuỗi" isActive={activeTab === 'history'} onClick={() => setActiveTab('history')} isOpen={isSidebarOpen} />
        </nav>
        <div className="p-4 border-t border-slate-800">
          <button onClick={onLogout} className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-red-400 hover:bg-slate-800 font-medium text-sm transition-all ${!isSidebarOpen && 'justify-center'}`}>
              <LogIn size={20} className="rotate-180" /> {isSidebarOpen && <span>Thoát</span>}
           </button>
        </div>
      </aside>

      <main className={`flex-1 p-8 transition-all duration-300 ${isSidebarOpen ? 'ml-64' : 'ml-20'}`}>
        <header className="flex justify-between items-center mb-8 bg-white p-4 rounded-2xl shadow-sm border border-slate-100 sticky top-4 z-40">
          <div className="flex items-center gap-4">
            <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="p-2 hover:bg-slate-100 rounded-lg text-slate-500"><Menu size={20} /></button>
            <div>
              <h1 className="text-2xl font-black text-slate-800 leading-none">{data.name}</h1>
              <div className="flex gap-2 mt-1"><span className="text-xs font-bold text-slate-400 bg-slate-100 px-2 py-0.5 rounded">Mã: {data.ticker}</span></div>
            </div>
          </div>
          <div className="flex items-center gap-4">
             {isLoading ? (
               <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100 text-slate-600 text-xs font-bold border border-slate-200 animate-pulse"><Loader2 size={14} className="animate-spin" /> Verifying...</div>
             ) : data.isVerified ? (
               <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-700 text-xs font-bold border border-emerald-100 shadow-sm animate-in zoom-in"><CheckCircle2 size={14} /> Verified by Blockchain</div>
             ) : (
               <button onClick={onRefreshChain} className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-50 text-amber-700 text-xs font-bold border border-amber-100 hover:bg-amber-100"><ShieldCheck size={14} /> Unverified</button>
             )}
          </div>
        </header>

        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
          {activeTab === 'dashboard' && <DashboardView data={data} isLoading={isLoading} />}
          {activeTab === 'analysis' && <AnalysisView />}
          {activeTab === 'history' && <HistoryView />}
        </div>
      </main>
    </div>
  );
}

// --- SUB-COMPONENTS ---
function DashboardView({ data, isLoading }) {
  if (isLoading) return <div className="h-[60vh] flex flex-col items-center justify-center text-slate-400"><Loader2 size={48} className="animate-spin text-emerald-500 mb-4" /><p className="font-medium animate-pulse">Đang gọi hàm getLatestReport()...</p><p className="text-xs mt-2 font-mono text-slate-300">Contract: 0x8f3...a12</p></div>;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        <div className="md:col-span-8 bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col md:flex-row items-center justify-between relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-8 opacity-5"><ShieldCheck size={180} /></div>
          <div className="z-10">
            <p className="text-sm text-slate-400 font-bold uppercase tracking-wider mb-2">Tổng điểm ESG (On-chain)</p>
            <div className="flex items-baseline gap-2"><span className="text-7xl font-black text-emerald-600 tracking-tighter">{data.score}</span><span className="text-2xl text-slate-300 font-bold">/100</span></div>
            <div className="mt-4"><div className="px-4 py-2 bg-slate-50 rounded-xl border border-slate-100 inline-block"><p className="text-[10px] text-slate-400 uppercase font-bold">Xếp hạng</p><p className="text-lg font-black text-slate-800">{data.rank}</p></div></div>
          </div>
          <div className="h-32 w-32 rounded-full border-[6px] border-emerald-500 border-r-emerald-100 flex items-center justify-center bg-white shadow-xl z-10"><div className="text-center"><span className="block text-xs font-bold text-slate-400">Hạng</span><span className="block text-xl font-black text-emerald-600">{data.rank === "Checking..." ? "--" : "Top 10"}</span></div></div>
        </div>

        <div className={`md:col-span-4 p-8 rounded-[2rem] shadow-xl text-white flex flex-col justify-between relative overflow-hidden transition-all duration-500 ${data.isVerified ? 'bg-indigo-600 shadow-indigo-200' : 'bg-slate-300 shadow-none grayscale'}`}>
          <div className="absolute -right-4 -bottom-4 bg-white/10 w-32 h-32 rounded-full blur-2xl"></div>
          <div>
            <p className="text-indigo-100 text-xs font-bold uppercase tracking-widest mb-1">Dữ liệu gốc</p>
            <h3 className="text-xl font-bold leading-tight">Báo cáo lưu trữ trên IPFS</h3>
            {data.ipfsHash ? <p className="text-indigo-100/70 text-[10px] mt-2 font-mono break-all bg-black/10 p-2 rounded-lg border border-white/10">Hash: {data.ipfsHash.substring(0, 20)}...</p> : <p className="text-white/70 text-xs mt-2">Chưa có dữ liệu.</p>}
          </div>
          {data.ipfsHash ? <a href={`https://ipfs.io/ipfs/${data.ipfsHash}`} target="_blank" className="mt-6 w-full bg-white text-indigo-700 py-3 px-4 rounded-xl font-bold text-sm hover:bg-indigo-50 flex items-center justify-center gap-2"><Download size={16} /> Tải từ IPFS</a> : <button disabled className="mt-6 w-full bg-white/20 text-white cursor-not-allowed py-3 px-4 rounded-xl font-bold text-sm">Chưa khả dụng</button>}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {data.metrics.map((item) => (
          <div key={item.id} className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
            <div className="flex items-center gap-3 mb-6"><div className={`p-3 rounded-xl ${item.color.replace('bg-', 'bg-').replace('500', '100')} ${item.color.replace('bg-', 'text-').replace('500', '600')}`}>{item.icon}</div><span className="font-bold text-slate-700">{item.label}</span></div>
            <div className="flex items-end justify-between mb-2"><span className="text-4xl font-black text-slate-800">{item.value}</span><span className="text-xs text-slate-400 font-bold mb-1">PTS</span></div>
            <div className="h-2 bg-slate-100 rounded-full overflow-hidden"><div className={`h-full ${item.color} rounded-full transition-all duration-1000`} style={{ width: `${item.value}%` }}></div></div>
          </div>
        ))}
      </div>
    </div>
  );
}

function AnalysisView() { return <div className="flex flex-col items-center justify-center min-h-[400px] bg-white p-12 rounded-[2rem] border-2 border-dashed border-slate-300 text-center"><FileText size={48} className="text-indigo-600 mb-4" /><h3 className="text-2xl font-bold text-slate-800">AI Agent Analysis</h3><p className="text-slate-500 mb-6">Upload báo cáo để AI chấm điểm.</p><button className="bg-slate-900 text-white px-6 py-3 rounded-xl font-bold">Tải tài liệu</button></div>; }
function HistoryView() { return <div className="bg-white p-8 rounded-[2rem] border border-slate-100"><h3 className="font-bold text-lg mb-4">Lịch sử chuỗi</h3><p className="text-slate-500">Chức năng đang cập nhật...</p></div>; }
function SidebarItem({ icon, label, isActive, onClick, isOpen }) { return <button onClick={onClick} className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm whitespace-nowrap ${isActive ? 'bg-emerald-600 text-white shadow-lg' : 'text-slate-400 hover:bg-slate-800'} ${!isOpen && 'justify-center px-0'}`}>{icon} {isOpen && <span>{label}</span>}</button>; }