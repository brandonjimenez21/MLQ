# Clase que define un Proceso con varios atributos
class Process:
    def __init__(self, label, burst_time, arrival_time, queue, priority):
        self.label = label  # Identificador del proceso
        self.burst_time = burst_time  # Tiempo de ráfaga de CPU (cuánto tiempo necesita en CPU)
        self.remaining_time = burst_time  # Tiempo restante de ejecución
        self.arrival_time = arrival_time  # Tiempo en que llega al sistema
        self.queue = queue  # Cola a la que pertenece (1, 2 o 3)
        self.priority = priority  # Prioridad del proceso (mayor valor = mayor prioridad)
        self.wait_time = 0  # Tiempo de espera en la cola antes de ser ejecutado
        self.turnaround_time = 0  # Tiempo total que pasa en el sistema (desde que llega hasta que termina)
        self.completion_time = 0  # Tiempo en el que finaliza la ejecución del proceso
        self.response_time = -1  # Tiempo de respuesta, se calcula solo una vez (cuando el proceso es atendido)

# Clase que define el planificador de colas multinivel (MLQ)
class MLQScheduler:
    def __init__(self, quantum1=3, quantum2=5):
        # Tres colas de procesos, cada una con su política de planificación
        self.queues = {1: [], 2: [], 3: []}
        self.quantum1 = quantum1  # Quantum para Round Robin en la cola 1 (RR con quantum 3)
        self.quantum2 = quantum2  # Quantum para Round Robin en la cola 2 (RR con quantum 5)
        self.time = 0  # Tiempo global del sistema (simula el reloj del CPU)

    # Método para agregar procesos a la cola correspondiente
    def add_process(self, process):
        self.queues[process.queue].append(process)

    # Método que planifica los procesos en una cola usando Round Robin (RR)
    def schedule_rr(self, queue, quantum):
        process_order = []  # Lista para almacenar el orden de ejecución de los procesos
        queue_list = self.queues[queue]  # Cola específica (1 o 2)

        while queue_list:
            process = queue_list.pop(0)  # Sacamos el primer proceso de la cola

            # Si el proceso llega después del tiempo actual, avanzamos el tiempo
            if process.arrival_time > self.time:
                self.time = process.arrival_time

            # Calculamos el tiempo de respuesta la primera vez que se ejecuta el proceso
            if process.response_time == -1:
                process.response_time = self.time - process.arrival_time

            # Si el proceso puede completarse dentro del quantum
            if process.remaining_time <= quantum:
                self.time += process.remaining_time  # Actualizamos el tiempo global
                process.completion_time = self.time  # Tiempo en que finaliza el proceso
                process.turnaround_time = process.completion_time - process.arrival_time  # Turnaround time
                process.wait_time = process.turnaround_time - process.burst_time  # Tiempo de espera
                process.remaining_time = 0  # El proceso ha terminado
            else:
                # Si el proceso no puede completarse, lo ejecutamos por el quantum y lo reenviamos a la cola
                process.remaining_time -= quantum
                self.time += quantum
                queue_list.append(process)  # El proceso vuelve a la cola

            process_order.append(process.label)  # Guardamos el proceso en el orden de ejecución

        return process_order  # Devolvemos el orden en que fueron ejecutados los procesos

    # Método que planifica los procesos de la cola 3 usando First-Come, First-Served (FCFS)
    def schedule_fcfs(self):
        process_order = []  # Lista para almacenar el orden de ejecución
        queue_list = self.queues[3]  # Cola 3 para FCFS

        while queue_list:
            process = queue_list.pop(0)  # Sacamos el primer proceso de la cola

            # Si el proceso llega después del tiempo actual, avanzamos el tiempo
            if process.arrival_time > self.time:
                self.time = process.arrival_time

            # Calculamos el tiempo de respuesta la primera vez que se ejecuta
            if process.response_time == -1:
                process.response_time = self.time - process.arrival_time

            # Ejecutamos el proceso hasta completarlo (en FCFS no hay interrupciones)
            self.time += process.remaining_time
            process.completion_time = self.time  # Tiempo en que finaliza el proceso
            process.turnaround_time = process.completion_time - process.arrival_time  # Turnaround time
            process.wait_time = process.turnaround_time - process.burst_time  # Tiempo de espera
            process.remaining_time = 0  # El proceso ha terminado
            process_order.append(process.label)  # Guardamos el proceso en el orden de ejecución

        return process_order  # Devolvemos el orden de ejecución

    # Método que coordina la ejecución de las tres colas
    def schedule(self):
        # Ejecutar Round Robin en la cola 1 con quantum 3
        rr1_order = self.schedule_rr(1, self.quantum1)

        # Ejecutar Round Robin en la cola 2 con quantum 5
        rr2_order = self.schedule_rr(2, self.quantum2)

        # Ejecutar FCFS en la cola 3
        fcfs_order = self.schedule_fcfs()

        # Devolver el orden combinado de ejecución
        return rr1_order + rr2_order + fcfs_order

# Función para leer los procesos desde un archivo de entrada
def read_processes_from_file(filename):
    processes = []
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('#'):
                continue  # Ignoramos las líneas de comentarios
            parts = line.strip().split(';')  # Dividimos los datos por ';'
            label, burst_time, arrival_time, queue, priority = parts
            processes.append(Process(label, int(burst_time), int(arrival_time), int(queue), int(priority)))
    return processes

# Función para escribir los resultados de la ejecución en un archivo de salida
def write_output_to_file(processes, filename):
    with open(filename, 'w') as file:
        file.write("# etiqueta; BT; AT; Q; Pr; WT; CT; RT; TAT\n")  # Escribimos la cabecera
        for process in processes:
            # Escribimos los datos de cada proceso en el archivo de salida
            file.write(f"{process.label}; {process.burst_time}; {process.arrival_time}; {process.queue}; "
                       f"{process.priority}; {process.wait_time}; {process.completion_time}; "
                       f"{process.response_time}; {process.turnaround_time}\n")
    
    # Calcular los promedios de los tiempos
    total_processes = len(processes)
    avg_wt = sum(p.wait_time for p in processes) / total_processes
    avg_ct = sum(p.completion_time for p in processes) / total_processes
    avg_rt = sum(p.response_time for p in processes) / total_processes
    avg_tat = sum(p.turnaround_time for p in processes) / total_processes
    
    # Escribir los promedios en el archivo
    with open(filename, 'a') as file:
        file.write(f"\nWT={avg_wt}; CT={avg_ct}; RT={avg_rt}; TAT={avg_tat};\n")

# Función principal que lee múltiples archivos de entrada, ejecuta el scheduler y genera la salida
def main():
    input_files = ['mlq001.txt', 'mlq002.txt', 'mlq003.txt']  # Lista de archivos de entrada
    
    for input_file in input_files:
        scheduler = MLQScheduler()  # Creamos un nuevo scheduler
        processes = read_processes_from_file(input_file)  # Leemos los procesos desde el archivo

        for process in processes:
            scheduler.add_process(process)  # Agregamos los procesos al scheduler

        execution_order = scheduler.schedule()  # Ejecutamos la planificación
        output_file = f'output_{input_file.split(".")[0]}.txt'  # Nombre del archivo de salida
        write_output_to_file(processes, output_file)  # Escribimos los resultados en el archivo

        print(f"Orden de ejecución para {input_file}: {execution_order}")  # Mostramos el orden de ejecución

# Ejecutar la función principal
if __name__ == "__main__":
    main()