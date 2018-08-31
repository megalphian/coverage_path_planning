import os

log_dir = './gtsp/solver_logs/'
julia = 'julia'

def solve(problem_name, solver_loc, cost_matrix, cluster_array):
	"""
	This function will generate appropriate files for GLNS
	solver and start the solver.

	:param problem_name: The name of the problem, useful for problem_names
	:param solver_loc: path to the solver
	:param cost_matrix: Matrix with costs
	:param cluster_array: Information about clusters
	:return tour: Tour
	"""

	num_nodes = len(cost_matrix)
	num_clusters = len(cluster_array)

	is_simple = False
	if is_simple:

		props_simp_dict = {'N': num_nodes,
						'M': num_clusters,
				   		'Symmetric': 'false',
				   		'Triangle': 'false'}

		with open(problem_name+".txt", "w") as f:
			# Write the problem properties first
			for k, v in props_simpl_dict.items():
				f.write(k+': '+str(v)+'\n')

			# Write the node in cluster information
			for i in range(num_clusters):
				row = ""
				for j in range(len(cluster_array[i])):
					row += "%d "%(cluster_array[i][j])

				row += "\n"
				f.write(row)

			# Write the cost matrix
			for i in range(num_nodes):
				row = ""
				for j in range(num_nodes):
					row += "%5d "%cost_matrix[i][j]
				f.write(row+"\n")
		os.system("cp "+problem_name+".txt "+'gtsp_related/')

	else:

		props_dict = { 
				'COMMENT': problem_name+': CPP using GTSP solver',
				'TYPE': 'AGTSP',
				'DIMENSION': num_nodes,
				'GTSP_SETS': num_clusters,
				'EDGE_WEIGHT_TYPE': 'EXPLICIT',
				'EDGE_WEIGHT_FORMAT': 'FULL_MATRIX'}

		# Write GTSP instance properties
		with open(problem_name+".gtsp", "w") as f:

			# the name has to come first or the heading isn't recognized
			f.write( 'NAME : ' + problem_name + '\n' )

			for k, v in props_dict.items():
				f.write(k+' : '+str(v)+'\n')


			f.write("EDGE_WEIGHT_SECTION\n")

			for i in range(num_nodes):
				row = ""
				for j in range(num_nodes):
					row += "%5d "%cost_matrix[i][j]

				f.write(row+"\n")
		
			f.write("GTSP_SET_SECTION\n")

			for i in range(num_clusters):
				row = "%d "%(i+1)
				for j in range(len(cluster_array[i])):
					if cluster_array[0][0] == 0:
						row += "%d "%(cluster_array[i][j]+1)
					else:
						row += "%d "%(cluster_array[i][j])

				row += "-1\n"
				f.write(row)

			f.write("EOF\n")
			f.write("")

		cur_dir = os.getcwd()

		# Move the files to GTSP solver location
		problemFile = log_dir + problem_name + '.gtsp'
		problemParams = ' -output=' + cur_dir + '/' + log_dir + problem_name + '.tour'
		os.system("cp "+problem_name+".gtsp "+problemFile)

		os.chdir(solver_loc)
		cmd = julia + ' ' + "./GLNScmd.jl " + cur_dir + '/' + problemFile + ' ' + problemParams
	
		#print("[%18s] Launching the GLKH solver."%time_keeping.current_time())
		os.system(cmd)	
		#print("[%18s] GLKH solver has finished."%time_keeping.current_time())

		# cleanup
		os.chdir(cur_dir)


def read_tour(problem_name):

	# Read in the results from the TSP solver results
	with open(log_dir+problem_name+'.tour', 'r') as f:
		for i in range(7):
			f.readline()

		tour = []
		str = f.readline()
		if "EOF" not in str and "-1" not in str:
			import re
			tourExp = re.compile('\[([0-9, ]+)\]')
			tour = [int(x)-1 for x in tourExp.search( str ).group(1).split(', ')]
			
	return tour