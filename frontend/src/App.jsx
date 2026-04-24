import { useEffect, useMemo, useState } from 'react'
import { API_BASE, fetchGraph, fetchHealth, fetchRequirements, fetchSampleTranscript, runPipeline, transcribeAudio } from './api'

const STAGES = [
  'clean_transcript',
  'summarise_interview',
  'generate_user_story',
  'generate_tasks',
  'review_duplicates',
  'export_excel'
]

function StatusPill({ status }) {
  const value = status || 'pending'
  return <span className={`pill pill-${value}`}>{value}</span>
}

function StageBoard({ stageStatus }) {
  return (
    <div className="card">
      <div className="section-header">
        <h2>Status view</h2>
        <span className="muted">Agent progression</span>
      </div>
      <div className="stage-grid">
        {STAGES.map(stage => (
          <div key={stage} className="stage-card">
            <div className="stage-name">{stage.replaceAll('_', ' ')}</div>
            <StatusPill status={stageStatus?.[stage]} />
          </div>
        ))}
      </div>
    </div>
  )
}

function StoryCard({ story }) {
  if (!story) return null
  return (
    <div className="card">
      <div className="section-header">
        <h2>Parent user story</h2>
        <span className="muted">{story.story_id}</span>
      </div>
      <div className="story-line"><strong>Title:</strong> {story.title}</div>
      <div className="story-line"><strong>As a</strong> {story.as_a}</div>
      <div className="story-line"><strong>I want</strong> {story.i_want}</div>
      <div className="story-line"><strong>So that</strong> {story.so_that}</div>
      <div className="story-line"><strong>Business value:</strong> {story.business_value}</div>
      <div className="story-line"><strong>Priority:</strong> {story.priority}</div>
      <div className="story-line"><strong>Narrative:</strong> {story.narrative}</div>
      <div>
        <strong>Acceptance criteria</strong>
        <ul>
          {story.acceptance_criteria.map(item => <li key={item}>{item}</li>)}
        </ul>
      </div>
    </div>
  )
}

function SummaryCard({ summary }) {
  if (!summary) return null
  const groups = [
    ['Problem', [summary.problem]],
    ['User goals', summary.user_goals],
    ['Pain points', summary.pain_points],
    ['Constraints', summary.constraints],
    ['Actors', summary.actors],
    ['Value signals', summary.signals_of_value]
  ]
  return (
    <div className="card">
      <div className="section-header">
        <h2>Interview summary</h2>
      </div>
      <div className="summary-grid">
        {groups.map(([label, items]) => (
          <div key={label} className="summary-panel">
            <h3>{label}</h3>
            <ul>
              {items.map(item => <li key={item}>{item}</li>)}
            </ul>
          </div>
        ))}
      </div>
    </div>
  )
}

function TasksTable({ tasks }) {
  if (!tasks?.length) return null
  return (
    <div className="card">
      <div className="section-header">
        <h2>Task-level requirements</h2>
        <span className="muted">{tasks.length} generated tasks</span>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Task</th>
              <th>Type</th>
              <th>Priority</th>
              <th>Owner hint</th>
              <th>Dependencies</th>
              <th>BDD / Gherkin</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map(task => (
              <tr key={task.task_id}>
                <td>
                  <strong>{task.task_id}</strong>
                  <div>{task.title}</div>
                  <div className="muted small">{task.description}</div>
                </td>
                <td>{task.task_type}</td>
                <td>{task.priority}</td>
                <td>{task.owner_hint}</td>
                <td>{task.dependencies.join(', ') || '—'}</td>
                <td>
                  <ul className="compact-list">
                    {task.gherkin.map(line => <li key={line}>{line}</li>)}
                  </ul>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function DuplicatesPanel({ duplicates }) {
  return (
    <div className="card">
      <div className="section-header">
        <h2>Consolidation hints</h2>
        <span className="muted">{duplicates?.length || 0} suggestions</span>
      </div>
      {!duplicates?.length ? (
        <div className="empty-state">No meaningful near-duplicates were detected.</div>
      ) : (
        <div className="duplicate-grid">
          {duplicates.map(item => (
            <div className="duplicate-card" key={`${item.task_id}-${item.possible_duplicate_of}`}>
              <div><strong>{item.task_id}</strong> ↔ <strong>{item.possible_duplicate_of}</strong></div>
              <div className="muted">{item.reason}</div>
              <div>{item.recommendation}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function RequirementsSearch({ rows, search, setSearch, resetData }) {
  return (
    <div className="card">
      <div className="section-header">
        <h2>Requirements dataset</h2>
        <input
          className="search-input"
          placeholder="Search titles, Gherkin, owners, status..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </div>
      <button onClick={resetData}>Reset Data</button>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Story</th>
              <th>Task</th>
              <th>Type</th>
              <th>Status</th>
              <th>Priority</th>
              <th>Dependencies</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(row => (
              <tr key={row.task_id}>
                <td>
                  <strong>{row.story_id}</strong>
                  <div>{row.story_title}</div>
                </td>
                <td>
                  <strong>{row.task_id}</strong>
                  <div>{row.task_title}</div>
                </td>
                <td>{row.task_type}</td>
                <td>{row.status}</td>
                <td>{row.priority}</td>
                <td>{row.dependencies || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function DependencyGraph({ graph }) {
  if (!graph?.nodes?.length) {
    return (
      <div className="card">
        <div className="section-header">
          <h2>Dependency graph</h2>
        </div>
        <div className="empty-state">Run the pipeline to populate the graph.</div>
      </div>
    )
  }

  const storyNodes = graph.nodes.filter(node => node.kind === 'story')
  const taskNodes = graph.nodes.filter(node => node.kind === 'task')

  const positionedStories = storyNodes.map((node, index) => ({
    ...node,
    x: 120,
    y: 80 + index * 180
  }))

  const positionedTasks = taskNodes.map((node, index) => ({
    ...node,
    x: 520,
    y: 60 + index * 110
  }))

  const byId = Object.fromEntries([...positionedStories, ...positionedTasks].map(node => [node.id, node]))

  return (
    <div className="card">
      <div className="section-header">
        <h2>Dependency graph</h2>
        <span className="muted">Stories to tasks plus task dependencies</span>
      </div>
      <svg viewBox="0 0 920 760" className="graph">
        {graph.edges.map((edge, index) => {
          const source = byId[edge.source]
          const target = byId[edge.target]
          if (!source || !target) return null
          return (
            <line
              key={`${edge.source}-${edge.target}-${index}`}
              x1={source.x + 170}
              y1={source.y + 24}
              x2={target.x}
              y2={target.y + 24}
              stroke="#95a4c6"
              strokeWidth="2"
            />
          )
        })}
        {[...positionedStories, ...positionedTasks].map(node => (
          <g key={node.id} transform={`translate(${node.x}, ${node.y})`}>
            <rect
              width="170"
              height="48"
              rx="14"
              fill={node.kind === 'story' ? '#dfefff' : '#ffffff'}
              stroke={node.kind === 'story' ? '#4d7cff' : '#94a3b8'}
            />
            <text x="12" y="18" className="graph-id">{node.id}</text>
            <text x="12" y="34" className="graph-label">
              {node.label.length > 22 ? `${node.label.slice(0, 22)}…` : node.label}
            </text>
          </g>
        ))}
      </svg>
    </div>
  )
}

export default function App() {
  const [health, setHealth] = useState(null)
  const [transcript, setTranscript] = useState('')
  const [result, setResult] = useState(null)
  const [rows, setRows] = useState([])
  const [graph, setGraph] = useState(null)
  const [search, setSearch] = useState('')
  const [audioFile, setAudioFile] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function loadDataset(term = '') {
    const [requirements, graphData] = await Promise.all([
      fetchRequirements(term),
      fetchGraph()
    ])
    setRows(requirements.items)
    setGraph(graphData)
  }

  useEffect(() => {
    async function bootstrap() {
      try {
        const [healthData, sample] = await Promise.all([
          fetchHealth(),
          fetchSampleTranscript()
        ])
        setHealth(healthData)
        setTranscript(sample.transcript)
        await loadDataset()
      } catch (err) {
        setError(err.message)
      }
    }
    bootstrap()
  }, [])

  useEffect(() => {
    const id = setTimeout(() => {
      loadDataset(search).catch(err => setError(err.message))
    }, 250)
    return () => clearTimeout(id)
  }, [search])

  async function handleTranscribe() {
    if (!audioFile) return
    setBusy(true)
    setError('')
    try {
      const data = await transcribeAudio(audioFile)
      setTranscript(data.transcript)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function handleRun() {
    setBusy(true)
    setError('')
    try {
      const data = await runPipeline(transcript)
      setResult(data)
      await loadDataset(search)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const exportPath = result?.export_path

  const resetData = async () => {
    if (!confirm("Reset all generated requirements?")) return;

    await fetch(`${API_BASE}/reset`, { method: "DELETE" });
    await loadDataset(search);
  };

  return (
    <div className="page">
      <header className="hero">
        <div>
          <div className="eyebrow">Agentic AI Demo</div>
          <h1>Teams interview to delivery-ready requirements</h1>
          <p className="hero-copy">
            Turn a transcript into a parent user story, technical tasks, BDD criteria,
            and an exported Excel workbook.
          </p>
        </div>
        <div className="hero-meta">
          <div><strong>Provider:</strong> {health?.provider || 'loading...'}</div>
          <div><strong>Model:</strong> {health?.model || 'loading...'}</div>
          <div><strong>Dataset rows:</strong> {rows.length}</div>
        </div>
      </header>

      <div className="grid two">
        <div className="card">
          <div className="section-header">
            <h2>Transcript input</h2>
            <button className="ghost" onClick={() => fetchSampleTranscript().then(d => setTranscript(d.transcript))}>
              Load sample
            </button>
          </div>
          <textarea
            value={transcript}
            onChange={e => setTranscript(e.target.value)}
            placeholder="Paste a Teams transcript here..."
            rows={18}
          />
          <div className="button-row">
            <button onClick={handleRun} disabled={busy || transcript.trim().length < 20}>
              {busy ? 'Running...' : 'Run pipeline'}
            </button>
          </div>
        </div>

        <div className="stack">
          <div className="card">
            <div className="section-header">
              <h2>Optional audio transcription</h2>
              <span className="muted">OpenAI speech-to-text path</span>
            </div>
            <input type="file" accept="audio/*" onChange={e => setAudioFile(e.target.files?.[0] || null)} />
            <div className="button-row">
              <button className="secondary" onClick={handleTranscribe} disabled={busy || !audioFile}>
                {busy ? 'Working...' : 'Transcribe audio'}
              </button>
            </div>
          </div>

          <StageBoard stageStatus={result?.stage_status || {}} />

          <div className="card">
            <div className="section-header">
              <h2>Output</h2>
            </div>
            {exportPath ? (
              <>
                <div><strong>Excel export:</strong> <code>{exportPath}</code></div>
                <div><strong>Dataset size:</strong> {result.dataset_size}</div>
              </>
            ) : (
              <div className="empty-state">No run yet.</div>
            )}
          </div>
        </div>
      </div>

      {error ? <div className="error-banner">{error}</div> : null}

      <div className="grid one">
        <SummaryCard summary={result?.interview_summary} />
        <StoryCard story={result?.user_story} />
        <TasksTable tasks={result?.tasks} />
        <DuplicatesPanel duplicates={result?.duplicates} />
        <DependencyGraph graph={graph} />
        <RequirementsSearch
          rows={rows}
          search={search}
          setSearch={setSearch}
          resetData={resetData}
        />
        {result?.cleaned_transcript ? (
          <div className="card">
            <div className="section-header">
              <h2>Cleaned transcript</h2>
            </div>
            <pre className="transcript-block">{result.cleaned_transcript}</pre>
          </div>
        ) : null}
      </div>
    </div>
  )
}
