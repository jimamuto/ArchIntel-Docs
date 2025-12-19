export default function Sidebar({ children }) {
  return (
    <aside style={{ width: 240, background: '#f5f5f5', padding: 16, height: '100vh', float: 'left' }}>
      <nav>
        <ul>
          <li><a href="/projects">Projects</a></li>
          {/* TODO: Add file/module tree navigation */}
        </ul>
      </nav>
      {children}
    </aside>
  );
}
