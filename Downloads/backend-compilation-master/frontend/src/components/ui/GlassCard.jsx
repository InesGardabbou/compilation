import { motion } from 'framer-motion';

const GlassCard = ({ children, className = '', animate = true, delay = 0 }) => {
  const content = (
    <div className={`glass-card p-5 ${className}`}>
      {children}
    </div>
  );

  if (!animate) return content;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
    >
      {content}
    </motion.div>
  );
};

export default GlassCard;
