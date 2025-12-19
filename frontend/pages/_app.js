import '../styles/globals.css';
import Sidebar from '../components/Sidebar';

export default function App({ Component, pageProps }) {
  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1 p-6">
        <Component {...pageProps} />
      </div>
    </div>
  );
}
