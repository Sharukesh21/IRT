import React from 'react'
import { NavLink } from 'react-router-dom'
import {
  Home,
  Activity,
  CheckSquare,
  Zap,
  BarChart3,
  Settings,
  BookOpen,
  Search,
  GitBranch,
  Target,
  Shield,
  FlaskConical,
  GitPullRequest,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useSystemStatus } from '@/hooks/useSystemStatus'

const navGroups = [
  {
    label: 'Dashboard',
    items: [
      { name: 'Overview', to: '/', icon: Home },
    ],
  },
  {
    label: 'Exam Simulator',
    items: [
      { name: 'Take Exam', to: '/exam', icon: BookOpen },
      { name: 'Event Traces', to: '/event-traces', icon: Activity },
      { name: 'State Inspector', to: '/state-inspector', icon: Search },
    ],
  },
  {
    label: 'Chaos Engineering',
    items: [
      { name: 'Failure Simulator', to: '/simulator', icon: Zap },
      { name: 'Metrics', to: '/metrics', icon: BarChart3 },
    ],
  },
  {
    label: 'Incident Intelligence',
    items: [
      { name: 'Incidents', to: '/incidents', icon: Shield },
      { name: 'Ingestion Lab', to: '/production-incidents', icon: FlaskConical },
    ],
  },
  {
    label: 'Regression',
    items: [
      { name: 'Regression Center', to: '/regression', icon: CheckSquare },
      { name: 'CI Dashboard', to: '/ci-regression', icon: GitPullRequest },
    ],
  },
  {
    label: 'Evaluation',
    items: [
      { name: 'Evaluation Center', to: '/evaluation', icon: Target },
    ],
  },
  {
    label: 'System',
    items: [
      { name: 'Settings', to: '/settings', icon: Settings },
    ],
  },
]

const NavSection: React.FC<{ label: string; items: { name: string; to: string; icon: React.ElementType }[] }> = ({ label, items }) => (
  <div className="mb-5">
    <p className="px-3 mb-1.5 text-[10px] font-semibold uppercase tracking-widest text-slate-400">{label}</p>
    {items.map((item) => (
      <NavLink
        key={item.name}
        to={item.to}
        end={item.to === '/'}
        className={({ isActive }) =>
          cn(
            'group flex items-center px-3 py-2.5 text-sm font-medium rounded-xl transition-all mb-0.5',
            isActive
              ? 'bg-black/8 text-slate-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.5)]'
              : 'text-slate-600 hover:bg-black/5 hover:text-slate-900'
          )
        }
      >
        {({ isActive }) => (
          <>
            <item.icon
              className={cn(
                'mr-3 h-4 w-4 flex-shrink-0 transition-colors',
                isActive ? 'text-violet-600' : 'text-slate-400 group-hover:text-violet-500'
              )}
            />
            {item.name}
          </>
        )}
      </NavLink>
    ))}
  </div>
)

export const Sidebar: React.FC = () => {
  const { environment } = useSystemStatus()

  return (
    <div className="flex h-full w-64 flex-col glass-sidebar z-20">
      {/* Logo */}
      <div className="flex h-16 items-center px-5 border-b border-black/5">
        <div className="flex items-center space-x-3">
          <div className="bg-violet-500/10 border border-violet-500/20 p-1.5 rounded-xl backdrop-blur-sm">
            <GitBranch className="h-5 w-5 text-violet-600" />
          </div>
          <div>
            <span className="text-sm font-bold text-slate-800 tracking-tight block">ITR Pipeline</span>
            <span className="text-[10px] text-slate-500 font-medium">Incident → Regression</span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-5 scrollbar-thin">
        {navGroups.map(group => (
          <NavSection key={group.label} label={group.label} items={group.items} />
        ))}
      </nav>

      {/* Environment Footer */}
      <div className="p-4 border-t border-black/5">
        <div className="flex items-center justify-between rounded-xl bg-white/40 border border-white/60 shadow-sm px-3 py-2.5 backdrop-blur-md">
          <div className="flex items-center space-x-2">
            <div className={cn(
              'h-2 w-2 rounded-full',
              environment !== 'unknown' ? 'bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.6)]' : 'bg-slate-400'
            )} />
            <span className="text-xs font-semibold text-slate-700 capitalize">{environment} env</span>
          </div>
          <span className="text-[10px] text-slate-500 font-mono font-medium">v1.0.0</span>
        </div>
      </div>
    </div>
  )
}
