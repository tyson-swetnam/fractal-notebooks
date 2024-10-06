import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.signal import welch
import sys

def generate_brownian_motion(N, scale=1.0):
    """
    Generate Brownian motion by cumulatively summing white noise.
    
    Parameters:
        N (int): Number of samples.
        scale (float): Scaling factor for the noise.
        
    Returns:
        brownian (numpy.ndarray): Generated Brownian motion signal.
    """
    white_noise = np.random.randn(N) * scale
    brownian = np.cumsum(white_noise)
    # Normalize the signal
    brownian = (brownian - np.mean(brownian)) / np.std(brownian)
    return brownian

def fractal_dimension_1d(signal, box_sizes=None):
    """
    Estimate the fractal dimension of a 1D signal using the Box-Counting method.
    
    Parameters:
        signal (numpy.ndarray): 1D signal.
        box_sizes (list or numpy.ndarray, optional): List of box sizes. If None, default sizes are used.
        
    Returns:
        D (float): Estimated fractal dimension.
    """
    if box_sizes is None:
        # Define box sizes logarithmically spaced
        box_sizes = np.floor(np.logspace(0.5, np.log10(len(signal)//2), num=10)).astype(int)
    
    box_sizes = box_sizes[box_sizes > 0]  # Ensure box sizes are positive
    N_boxes = []
    
    for size in box_sizes:
        # Number of boxes needed for current size
        count = int(np.ceil(len(signal) / size))
        N_boxes.append(count)
    
    log_sizes = np.log(1 / box_sizes)
    log_N = np.log(N_boxes)
    
    # Perform linear fit to estimate the slope (fractal dimension)
    coeffs = np.polyfit(log_sizes, log_N, 1)
    D = coeffs[0]
    
    return D

def create_brownian_motion_gif():
    """
    Create a GIF animation of Brownian motion with accompanying Fractal Dimension and PSD plots.
    """
    # Parameters
    N = 2048                   # Total number of samples
    num_frames = 200           # Number of frames in the GIF
    step = max(1, N // num_frames)  # Step size for each frame
    scale = 1.0                # Scaling factor for white noise
    
    # Generate Brownian motion
    brownian = generate_brownian_motion(N, scale=scale)
    
    # Precompute fractal dimensions and PSDs for all frames
    fractal_dims = []
    freqs_all = []
    psd_all = []
    
    print("Precomputing Fractal Dimensions and PSDs...")
    for i in range(1, num_frames + 1):
        idx = i * step
        if idx > N:
            idx = N
        segment = brownian[:idx]
        
        # Estimate fractal dimension
        D = fractal_dimension_1d(segment)
        fractal_dims.append(D)
        
        # Compute PSD using Welch's method
        freq, psd = welch(segment, nperseg=min(256, len(segment)))
        freqs_all.append(freq)
        psd_all.append(psd)
        
        if i % 20 == 0 or i == num_frames:
            print(f"Computed {i}/{num_frames} frames")
    
    # Set up the figure and axes
    fig, axs = plt.subplots(3, 1, figsize=(10, 12))
    
    # Time Domain Plot
    axs[0].set_title('Brownian Motion Signal')
    axs[0].set_xlabel('Sample')
    axs[0].set_ylabel('Amplitude')
    axs[0].set_xlim(0, N)
    axs[0].set_ylim(np.min(brownian) - 1, np.max(brownian) + 1)
    line1, = axs[0].plot([], [], color='black')
    
    # Fractal Dimension Plot
    axs[1].set_title('Fractal Dimension Over Time')
    axs[1].set_xlabel('Sample')
    axs[1].set_ylabel('Fractal Dimension')
    axs[1].set_xlim(0, N)
    axs[1].set_ylim(1, 2)  # Fractal dimension for 1D signals typically between 1 and 2
    line2, = axs[1].plot([], [], color='blue')
    
    # Power Spectral Density (PSD) Plot
    axs[2].set_title('Power Spectral Density (PSD)')
    axs[2].set_xlabel('Frequency')
    axs[2].set_ylabel('PSD')
    axs[2].set_xlim(0, 0.5)  # Normalized frequency (Nyquist frequency = 0.5)
    axs[2].set_ylim(0, None)  # Dynamic y-axis
    line3, = axs[2].plot([], [], color='red')
    
    plt.tight_layout()
    
    def init():
        """
        Initialize the animation by setting empty data.
        """
        line1.set_data([], [])
        line2.set_data([], [])
        line3.set_data([], [])
        return line1, line2, line3
    
    def update(frame):
        """
        Update function for animation frames.
        
        Parameters:
            frame (int): Current frame index.
            
        Returns:
            tuple: Updated plot lines.
        """
        # Update Time Domain Plot
        current_sample = (frame + 1) * step
        if current_sample > N:
            current_sample = N
        x_time = np.arange(current_sample)
        y_time = brownian[:current_sample]
        line1.set_data(x_time, y_time)
        
        # Update Fractal Dimension Plot
        x_fd = np.arange(frame + 1) * step
        if x_fd[-1] > N:
            x_fd[-1] = N
        y_fd = fractal_dims[:frame + 1]
        line2.set_data(x_fd, y_fd)
        
        # Update PSD Plot
        freq = freqs_all[frame]
        psd = psd_all[frame]
        line3.set_data(freq, psd)
        axs[2].set_ylim(0, max(psd) * 1.1)  # Adjust y-axis dynamically
        
        return line1, line2, line3
    
    # Create the animation
    print("Creating animation...")
    anim = FuncAnimation(fig, update, frames=num_frames, init_func=init, blit=False, interval=50)
    
    # Save the animation as a GIF
    print("Saving GIF... This may take a while.")
    try:
        anim.save('brownian_motion_animation.gif', writer='pillow', fps=20)
        print("GIF saved as 'brownian_motion_animation.gif'")
    except KeyboardInterrupt:
        print("\nGIF creation interrupted by user. Exiting gracefully...")
        plt.close(fig)
        sys.exit(0)
    
    plt.close(fig)  # Close the figure to free memory

if __name__ == "__main__":
    create_brownian_motion_gif()
