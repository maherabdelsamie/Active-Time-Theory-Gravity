import numpy as np
import matplotlib.pyplot as plt

# Constants
C = 299792458  # Speed of light in m/s
delta_t = 5
h = 6.62607015e-34  # Planck's constant in m^2 kg / s

class GlobalTime:
    def __init__(self, use_ath=True):
        self.phi_history = [0] * delta_t
        self.current_time = 0
        self.time_flow_rate = 1
        self.dt = 0.01
        self.time_flow_rates = []
        self.use_ath = use_ath  # Determine if ATH effects are applied

    def calculate_phi_derivative(self, energy_density):
        if not self.use_ath:
            return 0  # No φ modulation if ATH is not applied
        phi_delayed = self.phi_history[-delta_t]
        adaptive_factor = np.log1p(energy_density) * 0.05
        return adaptive_factor - 0.1 * phi_delayed

    def update_phi(self, energy_density):
        k1 = self.dt * self.calculate_phi_derivative(energy_density)
        k2 = self.dt * self.calculate_phi_derivative(energy_density)
        k3 = self.dt * self.calculate_phi_derivative(energy_density)
        k4 = self.dt * self.calculate_phi_derivative(energy_density)
        phi_update = (k1 + 2*k2 + 2*k3 + k4) / 6
        self.phi_history.append(self.phi_history[-1] + phi_update)
        if len(self.phi_history) > delta_t:
            self.phi_history.pop(0)

    def update_time_flow(self):
        if not self.use_ath:
            self.time_flow_rates.append(1)  # Constant time flow rate if ATH is not applied
            return
        current_phi = self.phi_history[-1]
        self.time_flow_rate = 1 + 0.05 * np.tanh(current_phi)
        self.time_flow_rates.append(self.time_flow_rate)

    def update_current_time(self):
        self.current_time += self.time_flow_rate * self.dt

class QuantumParticle:
    def __init__(self, state, velocity):
        self.state = np.array(state, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.H = np.eye(len(state))
        self.dilated_times = []

    def update_state(self, dt, global_time):
        lorentz_factor = 1 / np.sqrt(1 - np.linalg.norm(self.velocity)**2 / C**2)
        if global_time.use_ath:
            lorentz_factor_ath = lorentz_factor * (1 + global_time.phi_history[-1])
        else:
            lorentz_factor_ath = lorentz_factor
        effective_dt = dt * lorentz_factor_ath
        self.state = self.state + np.dot(self.H, self.state) * effective_dt
        self.state /= np.linalg.norm(self.state)

    def calculate_dilated_time(self, dt, global_time):
        lorentz_factor = 1 / np.sqrt(1 - np.linalg.norm(self.velocity)**2 / C**2)
        if global_time.use_ath:
            lorentz_factor_ath = lorentz_factor * (1 + global_time.phi_history[-1])
        else:
            lorentz_factor_ath = lorentz_factor
        dilated_time = dt * lorentz_factor_ath
        self.dilated_times.append(dilated_time)

class CesiumAtom:
    def __init__(self, initial_state):
        self.state = initial_state
        self.transition_frequencies = []

    def calculate_transitions(self, global_time):
        if global_time.use_ath:
            gamma_ath = (1 + global_time.phi_history[-1]) * np.sqrt(self.state)
        else:
            gamma_ath = np.sqrt(self.state)  # Classical behavior without ATH
        self.transition_frequencies.append(gamma_ath)

def run_simulation(use_active_time, max_iterations=1000):
    global_time = GlobalTime(use_ath=use_active_time)
    particles = [QuantumParticle([1.0, 0.0], np.random.uniform(-0.5, 0.5, 3) * C) for _ in range(10)]
    cesium_atoms = [CesiumAtom(np.random.uniform(0.1, 2.0)) for _ in range(5)]
    intrinsic_times = []

    for iteration in range(max_iterations):
        energy_density = np.mean([np.linalg.norm(p.velocity)**2 for p in particles])
        global_time.update_phi(energy_density)
        global_time.update_time_flow()
        global_time.update_current_time()

        for atom in cesium_atoms:
            atom.calculate_transitions(global_time)

        intrinsic_times.append(global_time.current_time)
        for particle in particles:
            particle.update_state(global_time.dt, global_time)
            particle.calculate_dilated_time(global_time.dt, global_time)

    return cesium_atoms, intrinsic_times, global_time.time_flow_rates, [p.dilated_times for p in particles]


def print_and_plot_results(use_ath, cesium_atoms, intrinsic_times, time_flow_rates, dilated_times):
    # Identifying the simulation type
    sim_type = "ATH" if use_ath else "Classical"
    print(f"--- Results for {sim_type} Simulation ---")
    
    # Printing Average Time Flow Rate
    avg_time_flow_rate = np.mean(time_flow_rates)
    print(f"Average Time Flow Rate: {avg_time_flow_rate:.4f}")

    # Printing Dilated Time Ranges for Particles
    for i, times in enumerate(dilated_times, start=1):
        min_time, max_time = np.min(times), np.max(times)
        print(f"Particle {i} Dilated Time Range: Min = {min_time:.4f}, Max = {max_time:.4f}")

    # Printing Average Transition Frequencies for Cesium Atoms
    for i, atom in enumerate(cesium_atoms, start=1):
        avg_freq = np.mean(atom.transition_frequencies)
        freq_range = np.min(atom.transition_frequencies), np.max(atom.transition_frequencies)
        print(f"Cesium Atom {i} Average Transition Frequency: {avg_freq:.4e} Hz, Range: {freq_range[0]:.4e} to {freq_range[1]:.4e} Hz")
    
    # Plotting
    plt.figure(figsize=(12, 8))

    plt.subplot(2, 2, 1)
    plt.plot(intrinsic_times, label=f'Intrinsic Time ({sim_type})')
    plt.xlabel('Iteration')
    plt.ylabel('Intrinsic Time')
    plt.title('Intrinsic Time Over Iterations')
    plt.legend()

    plt.subplot(2, 2, 2)
    plt.plot(time_flow_rates, label=f'Time Flow Rate ({sim_type})')
    plt.xlabel('Iteration')
    plt.ylabel('Time Flow Rate')
    plt.title('Time Flow Rate Over Iterations')
    plt.legend()

    plt.subplot(2, 2, 3)
    for i, times in enumerate(dilated_times, start=1):
        plt.plot(times, label=f'Particle {i} ({sim_type})')
    plt.xlabel('Iteration')
    plt.ylabel('Dilated Time')
    plt.title('Dilated Time for Particles')
    plt.legend()

    plt.subplot(2, 2, 4)
    for i, atom in enumerate(cesium_atoms, start=1):
        plt.plot(atom.transition_frequencies, label=f'Atom {i} ({sim_type})')
    plt.xlabel('Transition')
    plt.ylabel('Frequency (Hz)')
    plt.title('Transition Frequencies for Cesium Atoms')
    plt.legend()

    plt.tight_layout()
    plt.show()

# Running and comparing ATH vs. Classical simulations
for use_ath in [True, False]:
    cesium_atoms, intrinsic_times, time_flow_rates, dilated_times = run_simulation(use_active_time=use_ath, max_iterations=1000)
    print_and_plot_results(use_ath, cesium_atoms, intrinsic_times, time_flow_rates, dilated_times)
