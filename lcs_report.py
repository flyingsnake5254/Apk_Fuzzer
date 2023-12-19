import csv
import os
def lcs_length(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp[m][n]
def similarity(a, b):
    lcs_len = lcs_length(a, b)
    return lcs_len / max(len(a), len(b))


def process_csv(input_file, output_file):
    result = []

    with open(input_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            current_line = ''.join(row)
            if not any(similarity(current_line, ''.join(existing_line)) > 0.9 for existing_line in result):
                result.append(row)

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for line in result:
            writer.writerow(line)

def process_all_csvs(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            input_file = os.path.join(directory, filename)
            output_file = os.path.join(directory, filename.replace('.csv', '_output.csv'))
            process_csv(input_file, output_file)

process_all_csvs('report')