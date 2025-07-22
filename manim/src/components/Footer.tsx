import React from 'react';
import { motion } from 'framer-motion';

const Footer: React.FC = () => {
  return (
    <footer className="relative w-full bg-gray-50 text-black overflow-hidden pt-16 pb-6 font-funnel">
      {/* Animated Background Video */}
      

      {/* Content Overlay */}
      <motion.div
        className="relative z-10 max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-3 gap-8 text-center md:text-left"
        initial={{ opacity: 0, y: 40, filter: "blur(6px)" }}
        whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
        transition={{ duration: 1, ease: "easeOut" }}
        viewport={{ once: true }}
      >
        {/* Left Column */}
        <div>   
        <div className='flex items-center gap-1 m-1'>
          <div className='w-4 h-4 bg-black border rounded-full translate-y-0.5 '></div>
        <h1 className='text-xl font-medium'>Madio</h1>
        </div>
          <p className="text-gray-700 mt-2">
            Visualizing your equations. One prompt at a time.
          </p>
        </div>

        {/* Center Column */}
        <div>
          <h4 className="font-semibold text-lg">Quick Links</h4>
          <ul className="mt-2 space-y-1 text-gray-600">
            <li><a href="#mission" className="hover:text-white transition">Mission</a></li>
            <li><a href="#demo" className="hover:text-white transition">Demo</a></li>
            <li><a href="#get-started" className="hover:text-white transition">Get Started</a></li>
          </ul>
        </div>

        {/* Right Column */}
        <div>
          <h4 className="font-semibold text-lg">Connect</h4>
          <ul className="mt-2 space-y-1 text-gray-600">
            <li><a href="mailto:support@mathanim.ai" className="hover:text-white transition">Email</a></li>
            <li><a href="https://github.com/your-github" target="_blank" className="hover:text-white transition">GitHub</a></li>
            <li><a href="https://twitter.com/your-twitter" target="_blank" className="hover:text-white transition">Twitter</a></li>
          </ul>
        </div>
      </motion.div>

      {/* Bottom Bar */}
      <motion.div
        className="relative z-10 text-center text-gray-500 mt-12 text-sm"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        transition={{ delay: 0.3, duration: 1 }}
        viewport={{ once: true }}
      >
        © {new Date().getFullYear()} MathAnim. All rights reserved.
      </motion.div>
    </footer>
  );
};

export default Footer;
