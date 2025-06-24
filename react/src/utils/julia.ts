interface JuliaParams {
  cReal: number;
  cImaginary: number;
  maxIterations: number;
  width: number;
  height: number;
}

export class JuliaGenerator {
  private params: JuliaParams;

  constructor(params: JuliaParams) {
    this.params = params;
  }

  private juliaIteration(x: number, y: number): number {
    const { cReal, cImaginary, maxIterations } = this.params;
    let iteration = 0;

    while (x * x + y * y <= 4 && iteration < maxIterations) {
      const xTemp = x * x - y * y + cReal;
      y = 2 * x * y + cImaginary;
      x = xTemp;
      iteration++;
    }

    return iteration;
  }

  private getColor(iteration: number): string {
    if (iteration === this.params.maxIterations) {
      return '#000000'; // Black for points in the set
    }

    // Create smooth color gradient with different palette than Mandelbrot
    const normalized = iteration / this.params.maxIterations;
    const hue = (normalized * 300 + 180) % 360; // Shifted hue range
    const saturation = 85;
    const lightness = Math.min(30 + (normalized * 60), 85);
    
    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
  }

  async render(ctx: CanvasRenderingContext2D): Promise<void> {
    const { width, height } = this.params;
    const scale = 4; // Fixed scale for Julia sets
    
    const imageData = ctx.createImageData(width, height);
    const data = imageData.data;

    // Calculate in chunks to allow UI updates
    const chunkSize = 1000;
    let pixelIndex = 0;

    for (let py = 0; py < height; py++) {
      for (let px = 0; px < width; px++) {
        // Convert pixel coordinates to complex plane
        const x = (px - width / 2) * scale / width;
        const y = (py - height / 2) * scale / height;

        const iteration = this.juliaIteration(x, y);
        const color = this.getColor(iteration);
        
        // Convert HSL to RGB for ImageData
        const rgb = this.hslToRgb(color);
        const dataIndex = (py * width + px) * 4;
        
        data[dataIndex] = rgb.r;     // Red
        data[dataIndex + 1] = rgb.g; // Green
        data[dataIndex + 2] = rgb.b; // Blue
        data[dataIndex + 3] = 255;   // Alpha

        pixelIndex++;

        // Yield control periodically
        if (pixelIndex % chunkSize === 0) {
          await new Promise(resolve => setTimeout(resolve, 0));
        }
      }
    }

    ctx.putImageData(imageData, 0, 0);
  }

  private hslToRgb(hslString: string): { r: number; g: number; b: number } {
    // Parse HSL string like "hsl(240, 100%, 50%)"
    const match = hslString.match(/hsl\((\d+),\s*(\d+)%,\s*(\d+)%\)/);
    if (!match) return { r: 0, g: 0, b: 0 };

    const h = parseInt(match[1]) / 360;
    const s = parseInt(match[2]) / 100;
    const l = parseInt(match[3]) / 100;

    let r, g, b;

    if (s === 0) {
      r = g = b = l; // achromatic
    } else {
      const hue2rgb = (p: number, q: number, t: number) => {
        if (t < 0) t += 1;
        if (t > 1) t -= 1;
        if (t < 1/6) return p + (q - p) * 6 * t;
        if (t < 1/2) return q;
        if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
        return p;
      };

      const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
      const p = 2 * l - q;
      r = hue2rgb(p, q, h + 1/3);
      g = hue2rgb(p, q, h);
      b = hue2rgb(p, q, h - 1/3);
    }

    return {
      r: Math.round(r * 255),
      g: Math.round(g * 255),
      b: Math.round(b * 255)
    };
  }
}