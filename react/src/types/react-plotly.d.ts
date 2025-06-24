declare module 'react-plotly.js' {
  import { Component } from 'react';
  import { PlotData, Layout, Config } from 'plotly.js';

  export interface PlotParams {
    data: PlotData[];
    layout?: Partial<Layout>;
    config?: Partial<Config>;
    style?: React.CSSProperties;
    className?: string;
    useResizeHandler?: boolean;
    debug?: boolean;
    onInitialized?: (figure: any, graphDiv: HTMLElement) => void;
    onUpdate?: (figure: any, graphDiv: HTMLElement) => void;
    onPurge?: (figure: any, graphDiv: HTMLElement) => void;
    onError?: (err: any) => void;
    divId?: string;
    revision?: number;
  }

  export default class Plot extends Component<PlotParams> {}
}