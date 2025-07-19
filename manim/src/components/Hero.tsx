/* eslint-disable @typescript-eslint/ban-ts-comment */

import { motion, useScroll, useTransform, type Variant } from 'framer-motion';

function Hero() {
  const { scrollY } = useScroll();
  
  // Transform scroll position to rotation degrees
  const rotate = useTransform(scrollY, [0, 1000], [0, 360]);
  
  // Animation variants for text containers
  const textContainerVariants = {
    hidden: { opacity: 1 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.03, // Very little delay between letters
        delayChildren: 0.2
      }
    }
  };

  // Animation variants for individual letters
  const letterVariants: Variant = {
    //@ts-ignore
    hidden: { 
      x: -20, 
      opacity: 0, 
      filter: 'blur(8px)' 
    },
    visible: { 
      x: 0, 
      opacity: 1, 
      filter: 'blur(0px)',
      transition: {
        duration: 0.5,
        ease: [0.25, 0.46, 0.45, 0.94]
      }
    }
  };

  // Function to split text into individual letters
  const splitTextToLetters = (text : string) => {
    return text.split('').map((char, index) => (
         //@ts-ignore
      <motion.span key={index} variants={letterVariants} style={{ display: 'inline-block' }}>
        {char === ' ' ? '\u00A0' : char} {/* Preserve spaces */}
      </motion.span>
    ));
  };

  // Animation variants for the GIF
  const gifVariants = {
    hidden: { 
      scale: 0.6, 
      opacity: 0, 
      filter: 'blur(30px)' 
    },
    visible: { 
      scale: 1, 
      opacity: 1, 
      filter: 'blur(0px)',
      transition: {
        duration: 1.5,
        ease: 'backOut', // Pop effect
        delay: 0.4
      }
    }
  };

  // Container animation to orchestrate child animations
  const containerVariants = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: 0.5 // Stagger between heading, subtitle, and gif
      }
    }
  };

  return (
    <div className='h-screen  overflow-hidden'>
      {/* Add some content below to enable scrolling */}
      <div className='h-[200vh]'>
        <motion.div 
          className='flex flex-col items-center mt-60 min-h-screen relative'
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Main heading with letter-by-letter animation */}
          <motion.div>
            <motion.h1
              className='text-8xl font-funnel font-light'
              variants={textContainerVariants}
              initial="hidden"
              animate="visible"
            >
              {splitTextToLetters("Create for Madio")}
            </motion.h1>
          </motion.div>

          {/* Subtitle with letter-by-letter animation */}
          <motion.div className='mt-5 font-funnel'>
            <motion.h3
              className='text-gray-600'
              variants={textContainerVariants}
              initial="hidden"
              animate="visible"
               //@ts-ignore
              style={{ transition: { delayChildren: 0.1 } }}
            >
              {splitTextToLetters("make stunning mathematical animations with just a prompt.")}
            </motion.h3>
          </motion.div>

          {/* Mathematical figure with pop and rotation effects */}
          <motion.div>
            <motion.img 
              src='cube.gif' 
              alt='cube' 
              className='absolute right-1/3'
              width={600} 
              height={600}
               //@ts-ignore
              variants={gifVariants}
              style={{
                rotate: rotate, // Scroll-linked rotation
                transformOrigin: 'center center'
              }}
              whileHover={{
                scale: 1.05,
                transition: { duration: 0.3 }
              }}
            />
          </motion.div>
        </motion.div>

       
      </div>
      
    </div>
  );
}

export default Hero;