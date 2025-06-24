interface JuliaWebGLParams {
  cReal: number;
  cImaginary: number;
  centerX: number;
  centerY: number;
  zoom: number;
  maxIterations: number;
  width: number;
  height: number;
  colorScheme: 'classic' | 'fire' | 'ocean' | 'psychedelic' | 'grayscale';
}

export class JuliaWebGLGenerator {
  private canvas: HTMLCanvasElement;
  private gl: WebGLRenderingContext;
  private program!: WebGLProgram;
  private params: JuliaWebGLParams;
  private uniformLocations: { [key: string]: WebGLUniformLocation | null } = {};

  constructor(canvas: HTMLCanvasElement, params: JuliaWebGLParams) {
    this.canvas = canvas;
    this.params = params;
    
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (!gl) {
      throw new Error('WebGL not supported in this browser');
    }
    this.gl = gl as WebGLRenderingContext;

    this.initWebGL();
  }

  private initWebGL(): void {
    const vertexShaderSource = `
      attribute vec2 a_position;
      varying vec2 v_texCoord;
      
      void main() {
        gl_Position = vec4(a_position, 0.0, 1.0);
        v_texCoord = (a_position + 1.0) / 2.0;
      }
    `;

    const fragmentShaderSource = `
      precision highp float;
      
      uniform vec2 u_resolution;
      uniform vec2 u_center;
      uniform float u_zoom;
      uniform int u_maxIterations;
      uniform int u_colorScheme;
      uniform vec2 u_c; // Julia set parameter
      
      varying vec2 v_texCoord;
      
      vec3 getColor(int iterations, int maxIter) {
        if (iterations == maxIter) {
          return vec3(0.0, 0.0, 0.0); // Black for points in the set
        }
        
        float t = float(iterations) / float(maxIter);
        
        if (u_colorScheme == 0) { // classic (shifted hue for Julia)
          float hue = t * 6.28318 + 3.14159; // Shifted by PI for different colors than Mandelbrot
          return vec3(
            0.5 + 0.5 * cos(hue),
            0.5 + 0.5 * cos(hue + 2.094),
            0.5 + 0.5 * cos(hue + 4.188)
          );
        } else if (u_colorScheme == 1) { // fire
          return vec3(
            t,
            t * t * 0.8,
            t * t * t * 0.6
          );
        } else if (u_colorScheme == 2) { // ocean
          return vec3(
            t * 0.3,
            t * 0.7,
            0.8 + t * 0.2
          );
        } else if (u_colorScheme == 3) { // psychedelic
          float hue = t * 12.56636 + 1.57; // 4 * PI + offset for Julia sets
          return vec3(
            0.5 + 0.5 * sin(hue),
            0.5 + 0.5 * sin(hue + 1.57),
            0.5 + 0.5 * sin(hue + 3.14)
          );
        } else { // grayscale
          return vec3(t, t, t);
        }
      }
      
      void main() {
        // Start with the screen coordinate as the initial z value
        vec2 z = u_center + (v_texCoord - 0.5) * 4.0 / u_zoom;
        
        int iterations = 0;
        
        for (int i = 0; i < 1000; i++) {
          if (i >= u_maxIterations) break;
          
          if (dot(z, z) > 4.0) break;
          
          // Julia set iteration: z = z^2 + c (where c is constant)
          z = vec2(z.x * z.x - z.y * z.y, 2.0 * z.x * z.y) + u_c;
          iterations++;
        }
        
        vec3 color = getColor(iterations, u_maxIterations);
        gl_FragColor = vec4(color, 1.0);
      }
    `;

    // Create and compile shaders
    const vertexShader = this.createShader(this.gl.VERTEX_SHADER, vertexShaderSource);
    const fragmentShader = this.createShader(this.gl.FRAGMENT_SHADER, fragmentShaderSource);

    // Create and link program
    this.program = this.createProgram(vertexShader, fragmentShader);
    this.gl.useProgram(this.program);

    // Get uniform locations
    this.uniformLocations = {
      u_resolution: this.gl.getUniformLocation(this.program, 'u_resolution'),
      u_center: this.gl.getUniformLocation(this.program, 'u_center'),
      u_zoom: this.gl.getUniformLocation(this.program, 'u_zoom'),
      u_maxIterations: this.gl.getUniformLocation(this.program, 'u_maxIterations'),
      u_colorScheme: this.gl.getUniformLocation(this.program, 'u_colorScheme'),
      u_c: this.gl.getUniformLocation(this.program, 'u_c')
    };

    // Create a full-screen quad
    const positions = new Float32Array([
      -1, -1,
       1, -1,
      -1,  1,
       1,  1
    ]);

    const positionBuffer = this.gl.createBuffer();
    this.gl.bindBuffer(this.gl.ARRAY_BUFFER, positionBuffer);
    this.gl.bufferData(this.gl.ARRAY_BUFFER, positions, this.gl.STATIC_DRAW);

    const positionLocation = this.gl.getAttribLocation(this.program, 'a_position');
    this.gl.enableVertexAttribArray(positionLocation);
    this.gl.vertexAttribPointer(positionLocation, 2, this.gl.FLOAT, false, 0, 0);
  }

  private createShader(type: number, source: string): WebGLShader {
    const shader = this.gl.createShader(type);
    if (!shader) {
      throw new Error('Failed to create shader');
    }

    this.gl.shaderSource(shader, source);
    this.gl.compileShader(shader);

    if (!this.gl.getShaderParameter(shader, this.gl.COMPILE_STATUS)) {
      const info = this.gl.getShaderInfoLog(shader);
      this.gl.deleteShader(shader);
      throw new Error(`Shader compilation error: ${info}`);
    }

    return shader;
  }

  private createProgram(vertexShader: WebGLShader, fragmentShader: WebGLShader): WebGLProgram {
    const program = this.gl.createProgram();
    if (!program) {
      throw new Error('Failed to create program');
    }

    this.gl.attachShader(program, vertexShader);
    this.gl.attachShader(program, fragmentShader);
    this.gl.linkProgram(program);

    if (!this.gl.getProgramParameter(program, this.gl.LINK_STATUS)) {
      const info = this.gl.getProgramInfoLog(program);
      this.gl.deleteProgram(program);
      throw new Error(`Program linking error: ${info}`);
    }

    return program;
  }

  public updateParams(params: JuliaWebGLParams): void {
    this.params = params;
  }

  public render(): void {
    // Set canvas size
    this.canvas.width = this.params.width;
    this.canvas.height = this.params.height;
    this.gl.viewport(0, 0, this.params.width, this.params.height);

    // Set uniforms
    this.gl.uniform2f(this.uniformLocations.u_resolution, this.params.width, this.params.height);
    this.gl.uniform2f(this.uniformLocations.u_center, this.params.centerX, this.params.centerY);
    this.gl.uniform1f(this.uniformLocations.u_zoom, this.params.zoom);
    this.gl.uniform1i(this.uniformLocations.u_maxIterations, this.params.maxIterations);
    this.gl.uniform2f(this.uniformLocations.u_c, this.params.cReal, this.params.cImaginary);
    
    // Map color scheme to integer
    const colorSchemeMap: { [key: string]: number } = {
      'classic': 0,
      'fire': 1,
      'ocean': 2,
      'psychedelic': 3,
      'grayscale': 4
    };
    this.gl.uniform1i(this.uniformLocations.u_colorScheme, colorSchemeMap[this.params.colorScheme] || 0);

    // Clear and draw
    this.gl.clearColor(0, 0, 0, 1);
    this.gl.clear(this.gl.COLOR_BUFFER_BIT);
    this.gl.drawArrays(this.gl.TRIANGLE_STRIP, 0, 4);
  }

  public screenToComplex(screenX: number, screenY: number): { x: number; y: number } {
    const normalizedX = (screenX / this.params.width) - 0.5;
    const normalizedY = (screenY / this.params.height) - 0.5;
    
    const complexX = this.params.centerX + normalizedX * 4.0 / this.params.zoom;
    const complexY = this.params.centerY + normalizedY * 4.0 / this.params.zoom;
    
    return { x: complexX, y: complexY };
  }

  public dispose(): void {
    if (this.program) {
      this.gl.deleteProgram(this.program);
    }
  }
}