import "./App.css";
import Footer from "./components/Footer";
import Header from "./components/Header";
import Hero from "./components/Hero";
import Works from "./components/Works";
import Mission from "./components/Mission";

import { UserSync } from "./components/UserSync";

function App() {
  return (
    <div className="relative bg-white transition-colors duration-300">
      <UserSync />
      <Header />
      <Hero />
      <Works />
      <Mission />
      <Footer />
    </div>
  );
}

export default App;
