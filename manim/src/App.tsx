
import './App.css';
import Footer from './components/Footer';
import Header from './components/Header';
import Hero from './components/Hero';
import Mission from './components/Mission';
import Works from './components/Works';


function App() {
 
  return (
    <div className="relative bg-gray-50">
      <Header/>
      <Hero/>
      <Works/>
      <Mission/>
      <Footer/>
    </div>
  );
}

export default App;