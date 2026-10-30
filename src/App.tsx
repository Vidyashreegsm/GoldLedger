
import {
  LayoutDashboard,
  Users,
  Package,
  Scale,
  Wallet,
  FileText,
  Settings,
  Search,
  Bell,
  Plus,
  ArrowUpRight,
  ArrowDownRight,
  AlertTriangle,
  ChevronDown,
  Menu,
  X,
  Gem,
  CalendarDays,
  MoreHorizontal,
} from "lucide-react";
import { useState } from "react";
import "./App.css";

const navigation = [
  { name: "Dashboard", icon: LayoutDashboard },
  { name: "Karigars", icon: Users },
  { name: "Job Orders", icon: Package },
  { name: "Gold Ledger", icon: Scale },
  { name: "Payments", icon: Wallet },
  { name: "Reports", icon: FileText },
];

const jobs = [
  {
    id: "GL-2026-001",
    karigar: "Ramesh Kumar",
    initials: "RK",
    type: "Gold Chain",
    gold: "125.500 g",
    due: "Oct 31, 2026",
    status: "In Progress",
  },
  {
    id: "GL-2026-002",
    karigar: "Manjunath S",
    initials: "MS",
    type: "Temple Necklace",
    gold: "245.000 g",
    due: "Nov 01, 2026",
    status: "Pending",
  },
  {
    id: "GL-2026-003",
    karigar: "Suresh Babu",
    initials: "SB",
    type: "Gold Bangles",
    gold: "180.250 g",
    due: "Oct 29, 2026",
    status: "Overdue",
  },
  {
    id: "GL-2026-004",
    karigar: "Anil Kumar",
    initials: "AK",
    type: "Finger Rings",
    gold: "42.000 g",
    due: "Oct 28, 2026",
    status: "Completed",
  },
];

const activities = [
  {
    icon: Package,
    title: "New job order created",
    detail: "Gold chain · Ramesh Kumar",
    time: "10 minutes ago",
    color: "blue",
  },
  {
    icon: Scale,
    title: "Gold returned",
    detail: "45.250 g · Manjunath S",
    time: "1 hour ago",
    color: "green",
  },
  {
    icon: Wallet,
    title: "Payment recorded",
    detail: "₹12,500 · Suresh Babu",
    time: "3 hours ago",
    color: "gold",
  },
];

function App() {
  const [activePage, setActivePage] = useState("Dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [search, setSearch] = useState("");

  const filteredJobs = jobs.filter((job) =>
    `${job.id} ${job.karigar} ${job.type}`
      .toLowerCase()
      .includes(search.toLowerCase()),
  );

  return (
    <div className="app-shell">
      {sidebarOpen && (
        <button
          className="mobile-overlay"
          onClick={() => setSidebarOpen(false)}
          aria-label="Close menu"
        />
      )}

      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-mark">
            <Gem size={23} strokeWidth={1.8} />
          </div>
          <div>
            <h1>GoldLedger</h1>
            <span>JEWELLERY MANAGEMENT</span>
          </div>
          <button
            className="close-sidebar"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close sidebar"
          >
            <X size={20} />
          </button>
        </div>

        <div className="nav-label">WORKSPACE</div>

        <nav className="navigation">
          {navigation.map((item) => {
            const Icon = item.icon;

            return (
              <button
                key={item.name}
                className={`nav-item ${
                  activePage === item.name ? "active" : ""
                }`}
                onClick={() => {
                  setActivePage(item.name);
                  setSidebarOpen(false);
                }}
              >
                <Icon size={19} strokeWidth={1.8} />
                <span>{item.name}</span>

                {item.name === "Job Orders" && (
                  <span className="nav-count">12</span>
                )}
              </button>
            );
          })}
        </nav>

        <div className="sidebar-bottom">
          <div className="help-card">
            <div className="help-icon">
              <Gem size={18} />
            </div>
            <p>Need help managing your gold?</p>
            <span>Keep every gram accounted for.</span>
          </div>

          <button className="nav-item settings-item">
            <Settings size={19} />
            <span>Settings</span>
          </button>

          <div className="profile">
            <div className="profile-avatar">VS</div>

            <div className="profile-info">
              <strong>Vidya Jewellers</strong>
              <span>Administrator</span>
            </div>

            <MoreHorizontal size={20} className="profile-more" />
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="mobile-menu"
              onClick={() => setSidebarOpen(true)}
              aria-label="Open menu"
            >
              <Menu size={22} />
            </button>

            <div className="breadcrumb">
              <span>Workspace</span>
              <span className="breadcrumb-slash">/</span>
              <strong>{activePage}</strong>
            </div>
          </div>

          <div className="topbar-right">
            <div className="today-pill">
              <CalendarDays size={15} />
              <span>October 30, 2026</span>
            </div>

            <button
              className="icon-button notification-button"
              aria-label="Notifications"
            >
              <Bell size={19} />
              <span className="notification-dot" />
            </button>

            <div className="topbar-avatar">VS</div>
          </div>
        </header>

        <div className="page-content">
          <section className="welcome-section">
            <div>
              <div className="eyebrow">
                <span className="eyebrow-dot" />
                YOUR BUSINESS AT A GLANCE
              </div>

              <h2>
                Good evening, Vidya <span>✦</span>
              </h2>

              <p>
                Here's what's happening with your jewellery business today.
              </p>
            </div>

            <button className="primary-button">
              <Plus size={18} />
              New Job Order
            </button>
          </section>

          <section className="stats-grid">
            <div className="stat-card">
              <div className="stat-top">
                <div className="stat-icon gold-icon">
                  <Gem size={19} />
                </div>

                <span className="stat-trend positive">
                  <ArrowUpRight size={14} />
                  8.2%
                </span>
              </div>

              <div className="stat-label">Total Gold Issued</div>
              <div className="stat-value">
                2,845.75 <span>g</span>
              </div>

              <div className="stat-footer">
                <span className="stat-footer-dot gold-dot" />
                Across all active job orders
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-top">
                <div className="stat-icon blue-icon">
                  <Users size={19} />
                </div>

                <span className="stat-trend positive">
                  <ArrowUpRight size={14} />
                  3 new
                </span>
              </div>

              <div className="stat-label">Active Karigars</div>
              <div className="stat-value">24</div>

              <div className="stat-footer">
                <span className="stat-footer-dot blue-dot" />
                18 currently working
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-top">
                <div className="stat-icon purple-icon">
                  <Package size={19} />
                </div>

                <span className="stat-trend neutral">This month</span>
              </div>

              <div className="stat-label">Pending Job Orders</div>
              <div className="stat-value">38</div>

              <div className="stat-footer">
                <span className="stat-footer-dot purple-dot" />
                12 in progress · 26 pending
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-top">
                <div className="stat-icon red-icon">
                  <AlertTriangle size={19} />
                </div>

                <span className="stat-trend negative">
                  <ArrowUpRight size={14} />
                  Needs attention
                </span>
              </div>

              <div className="stat-label">Overdue Deliveries</div>
              <div className="stat-value">06</div>

              <div className="stat-footer">
                <span className="stat-footer-dot red-dot" />
                3 orders overdue by 2+ days
              </div>
            </div>
          </section>

          <section className="middle-grid">
            <div className="panel gold-overview">
              <div className="panel-heading">
                <div>
                  <h3>Gold Overview</h3>
                  <p>Gold accountability across your business</p>
                </div>

                <button className="period-select">
                  This month <ChevronDown size={15} />
                </button>
              </div>

              <div className="gold-balance">
                <div className="balance-copy">
                  <span className="balance-label">
                    Gold currently with karigars
                  </span>

                  <div className="balance-value">
                    1,284.50 <span>g</span>
                  </div>

                  <div className="balance-note">
                    <span className="balance-note-dot" />
                    <span>45.2% of total issued gold</span>
                  </div>
                </div>

                <div className="gold-ring">
                  <div className="gold-ring-inner">
                    <Gem size={23} />
                    <span>45.2%</span>
                  </div>
                </div>
              </div>

              <div className="gold-breakdown">
                <div className="breakdown-row">
                  <div className="breakdown-name">
                    <span className="legend-dot issued-dot" />
                    Gold issued
                  </div>
                  <strong>2,845.75 g</strong>
                </div>

                <div className="breakdown-row">
                  <div className="breakdown-name">
                    <span className="legend-dot returned-dot" />
                    Gold returned
                  </div>
                  <strong>1,561.25 g</strong>
                </div>

                <div className="breakdown-row">
                  <div className="breakdown-name">
                    <span className="legend-dot wastage-dot" />
                    Recorded wastage
                  </div>
                  <strong>12.80 g</strong>
                </div>
              </div>
            </div>

            <div className="panel activity-panel">
              <div className="panel-heading">
                <div>
                  <h3>Recent Activity</h3>
                  <p>Latest updates from your workspace</p>
                </div>

                <button className="text-button">
                  View all <ArrowUpRight size={15} />
                </button>
              </div>

              <div className="activity-list">
                {activities.map((activity, index) => {
                  const Icon = activity.icon;

                  return (
                    <div className="activity-item" key={index}>
                      <div className={`activity-icon ${activity.color}`}>
                        <Icon size={17} />
                      </div>

                      <div className="activity-copy">
                        <strong>{activity.title}</strong>
                        <span>{activity.detail}</span>
                      </div>

                      <div className="activity-time">{activity.time}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          </section>

          <section className="panel jobs-panel">
            <div className="panel-heading jobs-heading">
              <div>
                <h3>Recent Job Orders</h3>
                <p>Keep track of your latest karigar assignments</p>
              </div>

              <div className="job-actions">
                <div className="search-box">
                  <Search size={16} />

                  <input
                    type="text"
                    placeholder="Search orders..."
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                  />
                </div>

                <button className="text-button">
                  View all <ArrowUpRight size={15} />
                </button>
              </div>
            </div>

            <div className="table-wrap">
              <table className="jobs-table">
                <thead>
                  <tr>
                    <th>JOB ORDER</th>
                    <th>KARIGAR</th>
                    <th>JEWELLERY TYPE</th>
                    <th>GOLD WEIGHT</th>
                    <th>DUE DATE</th>
                    <th>STATUS</th>
                    <th />
                  </tr>
                </thead>

                <tbody>
                  {filteredJobs.map((job) => (
                    <tr key={job.id}>
                      <td>
                        <span className="job-id">{job.id}</span>
                      </td>

                      <td>
                        <div className="karigar-cell">
                          <div className="karigar-avatar">
                            {job.initials}
                          </div>
                          <span>{job.karigar}</span>
                        </div>
                      </td>

                      <td>{job.type}</td>

                      <td className="weight-cell">{job.gold}</td>

                      <td className="date-cell">{job.due}</td>

                      <td>
                        <span
                          className={`status-badge ${job.status
                            .toLowerCase()
                            .replace(" ", "-")}`}
                        >
                          <span />
                          {job.status}
                        </span>
                      </td>

                      <td>
                        <button
                          className="row-menu"
                          aria-label={`More options for ${job.id}`}
                        >
                          <MoreHorizontal size={19} />
                        </button>
                      </td>
                    </tr>
                  ))}

                  {filteredJobs.length === 0 && (
                    <tr>
                      <td colSpan={7} className="empty-state">
                        No matching job orders found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="table-footer">
              <span>
                Showing <strong>{filteredJobs.length}</strong> of{" "}
                <strong>38</strong> job orders
              </span>

              <button className="pagination-button" disabled>
                <ArrowDownRight size={14} />
                More orders
              </button>
            </div>
          </section>

          <footer className="page-footer">
            <span>© 2026 GoldLedger</span>

            <span>
              Built for trust. Designed for transparency. <Gem size={13} />
            </span>
          </footer>
        </div>
      </main>
    </div>
  );
}

export default App;
