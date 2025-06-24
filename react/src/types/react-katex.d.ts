declare module 'react-katex' {
  import { Component } from 'react';

  export interface KatexOptions {
    displayMode?: boolean;
    output?: 'html' | 'mathml' | 'htmlAndMathml';
    leqno?: boolean;
    fleqn?: boolean;
    throwOnError?: boolean;
    errorColor?: string;
    macros?: Record<string, string>;
    minRuleThickness?: number;
    colorIsTextColor?: boolean;
    maxSize?: number;
    maxExpand?: number;
    strict?: boolean | string | Function;
    trust?: boolean | Function;
    globalGroup?: boolean;
  }

  export interface MathProps {
    math: string;
    block?: boolean;
    errorColor?: string;
    renderError?: (error: Error) => React.ReactNode;
    settings?: KatexOptions;
  }

  export interface InlineMathProps extends Omit<MathProps, 'block'> {
    children?: string;
  }

  export interface BlockMathProps extends Omit<MathProps, 'block'> {
    children?: string;
  }

  export class InlineMath extends Component<InlineMathProps> {}
  export class BlockMath extends Component<BlockMathProps> {}
}