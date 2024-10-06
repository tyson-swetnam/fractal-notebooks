import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.signal import welch
import sys

def generate_pink_noise(N):
    """
    Generate 1/f pink noise by filtering white noise in the frequency domain.
    
    Parameters:
        N (int): Number of samples.
        
    Returns:
        pink (numpy.ndarray): Generated pink noise signal.
    """
    # Generate white noise
    white = np.random.randn(N)
    
    # Perform FFT
    f = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(N, d=1.0)
    
    # Avoid division by zero at the zero frequency
    freqs[0] = freqs[1] if len(freqs) > 1 else 1.0
    
    # Apply 1/f filter to get pink noise
    f_filtered = f / np.sqrt(freqs)
    
    # Perform inverse FFT to get time-domain signal
    pink = np.fft.irfft(f_filtered, n=N)
    
    # Normalize the signal
    pink = (pink - np.mean(pink)) / np.std(pink)
    
    return pink

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
    N = []
    
    for size in box_sizes:
        # Number of boxes needed for current size
        count = int(np.ceil(len(signal) / size))
        N.append(count)
    
    log_sizes = np.log(1 / box_sizes)
    log_N = np.log(N)
    
    # Perform linear fit to estimate the slope (fractal dimension)
    coeffs = np.polyfit(log_sizes, log_N, 1)
    D = coeffs[0]
    
    return D

def create_pink_noise_gif():
    """
    Create a GIF animation of pink noise with accompanying Fractal Dimension and PSD plots.
    """
    # Parameters
    N = 2048                   # Total number of samples
    num_frames = 200           # Number of frames in the GIF
    step = max(1, N // num_frames)  # Step size for each frame
    
    # Generate pink noise
    pink = generate_pink_noise(N)
    
    # Precompute fractal dimensions and PSDs for all frames
    fractal_dims = []
    freqs_all = []
    psd_all = []
    
    print("Precomputing Fractal Dimensions and PSDs...")
    for i in range(1, num_frames + 1):
        idx = i * step
        if idx > N:
            idx = N
        segment = pink[:idx]
        
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
    axs[0].set_title('Pink Noise Signal')
    axs[0].set_xlabel('Sample')
    axs[0].set_ylabel('Amplitude')
    axs[0].set_xlim(0, N)
    axs[0].set_ylim(np.min(pink) - 1, np.max(pink) + 1)
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
        y_time = pink[:current_sample]
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
    anim.save('pink_noise_animation.gif', writer='pillow', fps=20)
    print("GIF saved as 'pink_noise_animation.gif'")
    
    plt.close(fig)  # Close the figure to free memory

if __name__ == "__main__":
    create_pink_noise_gif()
