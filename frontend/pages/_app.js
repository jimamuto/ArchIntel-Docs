import Sidebar from '../components/Sidebar';

export default function App({ Component, pageProps }) {
  return (
    <div style={{ display: 'flex' }}>
      <Sidebar />
      <div style={{ flex: 1, padding: 24 }}>
        <Component {...pageProps} />
      </div>
    </div>
  );
}
