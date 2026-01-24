import { motion } from "framer-motion";
import React from "react";

const Mission: React.FC = () => {
  return (
    <div className="relative h-screen w-full overflow-hidden bg-white transition-colors duration-300">
      {/* Background Video with Blend Mode */}
      <video
        autoPlay
        loop
        muted
        playsInline
        className="absolute inset-0 w-full h-full object-cover mix-blend-luminosity opacity-30 z-0"
      >
        <source src="/orb.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>

      {/* Main Centered Title */}
      <motion.div
        className="z-10 flex items-center justify-center h-full relative"
        initial={{ opacity: 0, y: 20, filter: "blur(4px)" }}
        whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
        viewport={{ once: true, amount: 0.6 }}
        transition={{ duration: 1.2, ease: "easeOut" }}
      >
        <h1 className="text-black font-funnel text-7xl font-bold text-center">
          Mission
        </h1>
      </motion.div>

      {/* Left Text */}
      <motion.div
        className="absolute top-20 left-20 max-w-2xl"
        initial={{ opacity: 0, x: -50, filter: "blur(4px)" }}
        whileInView={{ opacity: 1, x: 0, filter: "blur(0px)" }}
        viewport={{ once: true, amount: 0.4 }}
        transition={{ delay: 0.3, duration: 1, ease: "easeOut" }}
      >
        <h2 className="text-gray-500 font-funnel text-2xl font-bold text-left">
          Empowering anyone to turn mathematical ideas into stunning visual
          animations with just a prompt.
        </h2>
      </motion.div>

      {/* Right Text */}
      <motion.div
        className="absolute bottom-20 right-20 max-w-2xl"
        initial={{ opacity: 0, x: 50, filter: "blur(4px)" }}
        whileInView={{ opacity: 1, x: 0, filter: "blur(0px)" }}
        viewport={{ once: true, amount: 0.4 }}
        transition={{ delay: 0.5, duration: 1, ease: "easeOut" }}
      >
        <h2 className="text-gray-500 font-funnel text-2xl font-bold text-right">
          Bridging the gap between imagination and visualization through
          AI-driven Manim generation.
        </h2>
      </motion.div>
    </div>
  );
};

export default Mission;
