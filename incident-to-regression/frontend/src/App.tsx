import { Routes, Route } from 'react-router-dom'
import { AppLayout } from './layouts/AppLayout'
import { OverviewPage } from './pages/OverviewPage'
import { SettingsPage } from './pages/SettingsPage'
import { ExamPage } from './pages/ExamPage'
import { EventTracePage } from './pages/EventTracePage'
import { StateInspectorPage } from './pages/StateInspectorPage'
import { SimulatorPage } from './pages/SimulatorPage'
import { MetricsPage } from './pages/MetricsPage'
import { IncidentDashboardPage } from './pages/IncidentDashboardPage'
import { IncidentDetailPage } from './pages/IncidentDetailPage'
import { RegressionCenterPage } from './pages/RegressionCenterPage'
import { RegressionTestDetailPage } from './pages/RegressionTestDetailPage'
import { ProductionIncidentsPage } from './pages/ProductionIncidentsPage'
import { CIRegressionDashboardPage } from './pages/CIRegressionDashboardPage'
import { EvaluationDashboardPage } from './pages/EvaluationDashboardPage'
import { TracesPage } from './pages/TracesPage'
import { TestRunsPage } from './pages/TestRunsPage'
import { ExperimentsPage } from './pages/ExperimentsPage'
import { ErrorBoundary } from './components/ui/ErrorBoundary'
import { ToastContainer } from './components/ui/Toast'

function App() {
  return (
    <ErrorBoundary>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<OverviewPage />} />
          {/* Phase 2 Exam Routes */}
          <Route path="exam" element={<ExamPage />} />
          <Route path="event-traces" element={<EventTracePage />} />
          <Route path="state-inspector" element={<StateInspectorPage />} />
          {/* Phase 3 */}
          <Route path="simulator" element={<SimulatorPage />} />
          <Route path="metrics" element={<MetricsPage />} />
          {/* Phase 4 Incident Intelligence */}
          <Route path="incidents" element={<IncidentDashboardPage />} />
          <Route path="incidents/:incidentId" element={<IncidentDetailPage />} />
          {/* Phase 5 Regression */}
          <Route path="regression" element={<RegressionCenterPage />} />
          <Route path="regression/:testId" element={<RegressionTestDetailPage />} />
          {/* Phase 6 Production Incidents & CI */}
          <Route path="production-incidents" element={<ProductionIncidentsPage />} />
          <Route path="ci-regression" element={<CIRegressionDashboardPage />} />
          {/* Phase 7 Evaluation */}
          <Route path="evaluation" element={<EvaluationDashboardPage />} />
          {/* Placeholders */}
          <Route path="traces" element={<TracesPage />} />
          <Route path="test-runs" element={<TestRunsPage />} />
          <Route path="experiments" element={<ExperimentsPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Routes>
      <ToastContainer />
    </ErrorBoundary>
  )
}

export default App
