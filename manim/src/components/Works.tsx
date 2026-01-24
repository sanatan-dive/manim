/* eslint-disable @typescript-eslint/ban-ts-comment */
import { ArrowUpRight, PlayCircle, X } from "lucide-react";
import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface Step {
  title: string;
  step: string;
  description: string;
}

const Works: React.FC = () => {
  const [selectedStep, setSelectedStep] = useState<number | null>(null);

  const steps: Step[] = [
    {
      title: "Prompt",
      step: "1",
      description:
        "Enter your mathematical concept or question to start the process.",
    },
    {
      title: "Analyze",
      step: "2",
      description:
        "Gemini processes your prompt to understand and structure the query.",
    },
    {
      title: "Generate",
      step: "3",
      description: "Manim Python code is created to visualize your concept.",
    },
    {
      title: "Animate",
      step: "4",
      description: "Watch the mathematical animation come to life.",
    },
  ];

  // Animation variants for blur fade-in
  const fadeIn = (delay: number) => ({
    hidden: { opacity: 0, y: 20, scale: 0.9, filter: "blur(8px)" },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      filter: "blur(0px)",
      transition: { duration: 0.6, ease: "easeOut" as const, delay },
    },
  });

  const staggerContainer = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
      },
    },
  };

  const descriptionVariants = {
    hidden: { opacity: 0, y: 20, filter: "blur(8px)" },
    visible: {
      opacity: 1,
      y: 0,
      filter: "blur(0px)",
      transition: { duration: 0.5, ease: "easeOut" as const, delay: 0.2 },
    },
    exit: {
      opacity: 0,
      y: 20,
      filter: "blur(8px)",
      transition: { duration: 0.3, ease: "easeIn" as const },
    },
  };

  return (
    <div className="min-h-screen bg-gray-50 relative overflow-hidden" id="works">
      {/* Dotted Background with Top/Bottom Fade */}
      <div
        className="absolute inset-0 z-0"
        style={{
          background: "#f9fafb",
          backgroundImage:
            "radial-gradient(circle at 2px 2px, rgba(0, 0, 0, 0.20) 2px, transparent 0)",
          backgroundSize: "40px 35px",
          maskImage:
            "linear-gradient(to bottom, transparent, black 30%, black 80%, transparent)",
          WebkitMaskImage:
            "linear-gradient(to bottom, transparent, black 20%, black 80%, transparent)",
        }}
      />

      {/* Main Content */}
      <div className="relative z-10 ">
        {/* Header Section */}
        <motion.div
          className="flex items-center justify-between px-8"
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.5 }}
        >
          {/* @ts-ignore */}
          <motion.div variants={fadeIn(0.2)}>
            <img
              src="3dcube.png"
              width={"30%"}
              height={"30%"}
              alt="3D cube illustration"
              className="m-8 mt-20"
            />
          </motion.div>
          {/* @ts-ignore */}
          <motion.div variants={fadeIn(0.4)} className="ml-32 mt-20">
            <h1 className="text-9xl font-funnel">How does it work?</h1>
          </motion.div>
        </motion.div>

        {/* Content Section */}
        <motion.div
          className="flex items-center justify-between px-8"
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.5 }}
        >
          {/* Text Content */}
          {/* @ts-ignore */}
          <motion.div variants={fadeIn(0.6)} className="flex-1 max-w-2xl">
            <h2 className="text-xl font-funnel leading-relaxed mt-8">
              Our platform transforms your mathematical ideas into stunning
              animations. Enter a prompt, let Gemini analyze it, generate Manim
              Python code, and watch your concept come to life as an engaging
              visualization.
            </h2>
          </motion.div>

          {/* Buttons Section */}
          {/* @ts-ignore */}
          <motion.div
            variants={fadeIn(0.8)}
            className="flex items-center gap-6 mr-21 "
          >
            {/* Sign Up Button */}
            <div className="bg-white text-black border font-bold font-funnel px-6 py-3 text-xl rounded-full hover:bg-gray-50 transition-all duration-200 cursor-pointer flex gap-2 items-center italic">
              <button>Sign Up</button>
              <ArrowUpRight className="w-5 h-5" />
            </div>

            {/* Glass "See ability" Button */}
            <button className="group relative overflow-hidden">
              <div className="flex items-center px-6 py-3 rounded-full bg-gray-100  backdrop-blur-sm border border-white hover:bg-black/5 active:scale-95 transition-all duration-300 ease-out relative">
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-white/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <PlayCircle className="w-8 h-8 mr-3 text-black group-hover:text-black group-hover:scale-105 transition-all duration-300 ease-out relative z-10" />
                <h2 className="text-lg font-bold italic text-black group-hover:text-black transition-all duration-300 ease-out relative z-10 tracking-wide font-funnel">
                  See ability
                </h2>
              </div>
            </button>
          </motion.div>
        </motion.div>

        {/* Workflow Steps Section */}
        <motion.div
          className="flex flex-col md:flex-row justify-center gap-8 px-8 mt-32 "
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.5 }}
        >
          {steps.map((item, index) => (
            <motion.div
              key={index}
              className="flex flex-col items-center group cursor-pointer"
              onClick={() => setSelectedStep(index)}
              aria-label={`View details for ${item.title} step`}
              //@ts-ignore
              variants={fadeIn(0.2 * (index + 1))}
            >
              <div
                className={`w-24 h-24 rounded-full bg-black/5 z-50 backdrop-blur-sm border border-white flex items-center justify-center hover:bg-black/z0 hover:scale-105 ${
                  selectedStep === index ? "scale-110 bg-black/10" : ""
                } transition-all duration-300 ease-out`}
              >
                <span className="text-2xl font-bold font-funnel text-black">
                  {item.step}
                </span>
              </div>
              <h3 className="text-lg font-bold italic text-black font-funnel mt-4">
                {item.title}
              </h3>
            </motion.div>
          ))}
        </motion.div>

        {/* Description Section */}
        <AnimatePresence>
          {selectedStep !== null && (
            <motion.div
              className="mt-8 px-8 flex justify-center"
              //@ts-ignore
              variants={descriptionVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
            >
              <div className="relative max-w-2xl w-full bg-black/5 backdrop-blur-sm border border-white rounded-2xl p-6">
                <button
                  className="absolute top-4 right-4 text-black hover:text-gray-700 transition-colors"
                  onClick={() => setSelectedStep(null)}
                  aria-label="Close description"
                >
                  <X className="w-6 h-6" />
                </button>
                <h3 className="text-xl font-bold italic text-black font-funnel mb-4">
                  {steps[selectedStep].title}
                </h3>
                <p className="text-lg text-black font-funnel leading-relaxed">
                  {steps[selectedStep].description}
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default Works;
