import matplotlib.pyplot as plt

def plot_scores(df):
    plt.figure()
    plt.bar(df["work_id"], df["avg_score"])
    plt.title("Work Scores")
    plt.show()