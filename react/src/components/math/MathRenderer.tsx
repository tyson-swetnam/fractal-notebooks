import React from 'react';
import 'katex/dist/katex.min.css';
import { InlineMath, BlockMath } from 'react-katex';

interface MathRendererProps {
  math: string;
  block?: boolean;
  className?: string;
}

export const MathRenderer: React.FC<MathRendererProps> = ({ 
  math, 
  block = false, 
  className 
}) => {
  try {
    if (block) {
      return (
        <div className={className}>
          <BlockMath math={math} />
        </div>
      );
    } else {
      return (
        <span className={className}>
          <InlineMath math={math} />
        </span>
      );
    }
  } catch (error) {
    console.error('Error rendering math:', error);
    return (
      <span className={`math-error ${className || ''}`}>
        [Math Error: {math}]
      </span>
    );
  }
};

// Convenience components for common use cases
export const InlineMathRenderer: React.FC<{ children: string; className?: string }> = ({ 
  children, 
  className 
}) => (
  <MathRenderer math={children} block={false} className={className} />
);

export const BlockMathRenderer: React.FC<{ children: string; className?: string }> = ({ 
  children, 
  className 
}) => (
  <MathRenderer math={children} block={true} className={className} />
);