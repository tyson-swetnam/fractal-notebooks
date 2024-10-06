import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.signal import welch
import sys

def simulate_wave_tide_data(
    total_days=28,
    sampling_interval_minutes=10,
    tide_period_hours=12,
    wave_periods_hours=[0.25, 0.5, 1.0, 2.0],
    tide_amplitude=1.0,
    wave_amplitudes=[0.9, 0.5, 0.3, 0.2],
    noise_std=0.15
):
    """
    Simulate wave and tide height data over a specified number of days.

    Parameters:
        total_days (int): Number of days to simulate.
        sampling_interval_minutes (int): Sampling interval in minutes.
        tide_period_hours (float): Period of the tide in hours.
        wave_periods_hours (list of float): Periods of the waves in hours.
        tide_amplitude (float): Amplitude of the tide.
        wave_amplitudes (list of float): Amplitudes of the waves.
        noise_std (float): Standard deviation of the added Gaussian noise.

    Returns:
        time (numpy.ndarray): Time array in hours.
        signal (numpy.ndarray): Simulated wave and tide signal.
    """
    # Total number of samples
    total_minutes = total_days * 24 * 60
    num_samples = int(total_minutes / sampling_interval_minutes) + 1

    # Time array in hours
    time = np.linspace(0, total_days * 24, num_samples)

    # Initialize signal with zeros
    signal = np.zeros(num_samples)

    # Add tide component (dominant sine wave)
    tide_frequency = 1 / tide_period_hours  # cycles per hour
    signal += tide_amplitude * np.sin(2 * np.pi * tide_frequency * time)

    # Add wave components (multiple sine waves with shorter periods)
    for amp, period in zip(wave_amplitudes, wave_periods_hours):
        wave_frequency = 1 / period  # cycles per hour
        signal += amp * np.sin(2 * np.pi * wave_frequency * time)

    # Add Gaussian noise
    noise = np.random.normal(0, noise_std, num_samples)
    signal += noise

    # Normalize the signal to have zero mean and unit variance
    signal = (signal - np.mean(signal)) / np.std(signal)

    return time, signal

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

def create_wave_tide_gif():
    """
    Create a GIF animation of simulated wave and tide data with accompanying Fractal Dimension and PSD plots.
    """
    # Simulation Parameters
    total_days = 28
    sampling_interval_minutes = 10
    tide_period_hours = 12
    wave_periods_hours = [0.5, 1.0, 2.0]
    tide_amplitude = 1.0
    wave_amplitudes = [0.5, 0.3, 0.2]
    noise_std = 0.1

    # Generate simulated wave and tide data
    time, signal = simulate_wave_tide_data(
        total_days=total_days,
        sampling_interval_minutes=sampling_interval_minutes,
        tide_period_hours=tide_period_hours,
        wave_periods_hours=wave_periods_hours,
        tide_amplitude=tide_amplitude,
        wave_amplitudes=wave_amplitudes,
        noise_std=noise_std
    )

    # Parameters for Animation
    num_frames = 200
    step = max(1, len(signal) // num_frames)

    # Precompute fractal dimensions and PSDs for all frames
    fractal_dims = []
    freqs_all = []
    psd_all = []

    print("Precomputing Fractal Dimensions and PSDs...")
    for i in range(1, num_frames + 1):
        idx = i * step
        if idx > len(signal):
            idx = len(signal)
        segment = signal[:idx]

        # Estimate fractal dimension
        D = fractal_dimension_1d(segment)
        fractal_dims.append(D)

        # Compute PSD using Welch's method
        freq, psd = welch(segment, fs=1/(sampling_interval_minutes/60))  # Convert sampling interval to Hz
        freqs_all.append(freq)
        psd_all.append(psd)

        if i % 20 == 0 or i == num_frames:
            print(f"Computed {i}/{num_frames} frames")

    # Set up the figure and axes
    fig, axs = plt.subplots(3, 1, figsize=(14, 18))

    # Time Domain Plot
    axs[0].set_title('Simulated Wave and Tide Signal')
    axs[0].set_xlabel('Time (Hours)')
    axs[0].set_ylabel('Normalized Height')
    axs[0].set_xlim(0, total_days * 24)
    axs[0].set_ylim(np.min(signal) - 0.5, np.max(signal) + 0.5)
    line1, = axs[0].plot([], [], color='blue')

    # Fractal Dimension Plot
    axs[1].set_title('Fractal Dimension Over Time')
    axs[1].set_xlabel('Time (Hours)')
    axs[1].set_ylabel('Fractal Dimension')
    axs[1].set_xlim(0, total_days * 24)
    axs[1].set_ylim(1, 2.5)  # Adjusted based on expected fractal dimension range
    line2, = axs[1].plot([], [], color='green')

    # Power Spectral Density (PSD) Plot
    axs[2].set_title('Power Spectral Density (PSD)')
    axs[2].set_xlabel('Frequency (Hz)')
    axs[2].set_ylabel('PSD (V**2/Hz)')
    # Determine Nyquist frequency
    fs = 1 / (sampling_interval_minutes / 60)  # Sampling frequency in Hz
    nyquist = fs / 2
    axs[2].set_xlim(0, nyquist)
    axs[2].set_ylim(0, None)  # Dynamic y-axis based on data
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
        current_idx = (frame + 1) * step
        if current_idx > len(signal):
            current_idx = len(signal)
        x_time = time[:current_idx]
        y_time = signal[:current_idx]
        line1.set_data(x_time, y_time)
        # No need to adjust x-axis limits; they are fixed

        # Update Fractal Dimension Plot
        x_fd = time[:frame + 1]
        y_fd = fractal_dims[:frame + 1]
        line2.set_data(x_fd, y_fd)
        # No need to adjust x-axis limits; they are fixed

        # Update PSD Plot
        freq = freqs_all[frame]
        psd = psd_all[frame]
        line3.set_data(freq, psd)
        axs[2].set_ylim(0, max(psd) * 1.1)  # Adjust y-axis dynamically based on current PSD

        return line1, line2, line3

    # Create the animation
    print("Creating animation...")
    anim = FuncAnimation(fig, update, frames=num_frames, init_func=init, blit=False, interval=100)

    # Save the animation as a GIF
    print("Saving GIF... This may take a while.")
    try:
        anim.save('wave_tide_animation.gif', writer='pillow', fps=10)
        print("GIF saved as 'wave_tide_animation.gif'")
    except KeyboardInterrupt:
        print("\nGIF creation interrupted by user. Exiting gracefully...")
        plt.close(fig)
        sys.exit(0)

    plt.close(fig)  # Close the figure to free memory

if __name__ == "__main__":
    create_wave_tide_gif()
