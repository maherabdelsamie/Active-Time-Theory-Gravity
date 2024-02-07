import numpy as np

# Constants
C = 299792458  # Speed of light in m/s
delta_t = 5
h = 6.62607015e-34  # Planck's constant in m^2 kg / s

class GlobalTime:
    def __init__(self):
        self.phi_history = [0] * delta_t
        self.current_time = 0
        self.time_flow_rate = 1
        self.dt = 0.01
        self.time_flow_rates = []  # Initialize the time flow rates list here

    def calculate_phi_derivative(self, energy_density):
        phi_delayed = self.phi_history[-delta_t]
        adaptive_factor = 0.05 * energy_density
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
        current_phi = self.phi_history[-1]
        self.time_flow_rate = 1 + 0.05 * np.tanh(current_phi)
        self.time_flow_rates.append(self.time_flow_rate)  # Correctly append to the initialized list

    def update_current_time(self):
        self.current_time += self.time_flow_rate * self.dt

class QuantumParticle:
    def __init__(self, state, velocity):
        self.state = np.array(state, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.H = np.eye(len(state))  # Hamiltonian matrix as a placeholder
        self.dilated_times = []

    def update_state(self, dt, global_time):
        lorentz_factor = 1 / np.sqrt(1 - np.linalg.norm(self.velocity)**2 / C**2)
        lorentz_factor_ath = lorentz_factor * (1 + global_time.phi_history[-1])
        effective_dt = dt * lorentz_factor_ath
        self.state = self.state + np.dot(self.H, self.state) * effective_dt
        self.state /= np.linalg.norm(self.state)  # Normalize the state vector

    def calculate_dilated_time(self, dt, global_time):
        lorentz_factor = 1 / np.sqrt(1 - np.linalg.norm(self.velocity)**2 / C**2)
        lorentz_factor_ath = lorentz_factor * (1 + global_time.phi_history[-1])
        dilated_time = dt * lorentz_factor_ath
        self.dilated_times.append(dilated_time)

class CesiumAtom:
    def __init__(self):
        self.energy_levels = [-1.84e-23, -1.81e-23, -1.78e-23]

    def calculate_transitions(self, global_time):
        gamma_ath = 1 * (1 + global_time.phi_history[-1])  # Apply ATH effect
        self.transition_frequencies = {}
        for i in range(len(self.energy_levels)):
            for j in range(i+1, len(self.energy_levels)):
                adjusted_energy_i = self.energy_levels[i] * gamma_ath
                adjusted_energy_j = self.energy_levels[j] * gamma_ath
                freq = (adjusted_energy_j - adjusted_energy_i) / h
                self.transition_frequencies[(i, j)] = freq

def run_simulation(use_active_time, max_iterations=1000):
    global_time = GlobalTime()
    cesium_atoms = [CesiumAtom() for _ in range(5)]
    particles = [QuantumParticle([1.0, 0.0], np.random.uniform(-0.1, 0.1, 3) * C * 0.99) for _ in range(5)]
    intrinsic_times = []

    for iteration in range(max_iterations):
        energy_density = np.mean([np.linalg.norm(p.velocity)**2 for p in particles])
        if use_active_time:
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

def print_simulation_results(cesium_atoms, intrinsic_times, time_flow_rates, dilated_times):
    avg_time_flow_rate = np.mean(time_flow_rates)
    print(f"Average Time Flow Rate: {avg_time_flow_rate:.4f}")
    dilated_time_ranges = [(np.min(times), np.max(times)) for times in dilated_times]
    for i, (min_time, max_time) in enumerate(dilated_time_ranges, start=1):
        print(f"Particle {i} Dilated Time Range: Min = {min_time:.4f}, Max = {max_time:.4f}")
    for i, atom in enumerate(cesium_atoms, start=1):
        avg_freq = np.mean(list(atom.transition_frequencies.values()))
        freq_range = (np.min(list(atom.transition_frequencies.values())), np.max(list(atom.transition_frequencies.values())))
        print(f"Cesium Atom {i} Average Transition Frequency: {avg_freq:.4e} Hz, Range: {freq_range[0]:.4e} to {freq_range[1]:.4e} Hz")

# Example run and results
cesium_atoms, intrinsic_times, time_flow_rates, dilated_times = run_simulation(use_active_time=True, max_iterations=1000)
print_simulation_results(cesium_atoms, intrinsic_times, time_flow_rates, dilated_times)
