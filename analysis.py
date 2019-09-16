def paired_analysis_idx(array_length):
    """
    This function is to grap two element in each round. 
    The title should has the same length as array representing array element title
    """
    # total_num = array_length * array_length / 2
    output = []
    for i in range(array_length):
        for j in range(i+1, array_length):
            output.append([i,j])
    return(output)
