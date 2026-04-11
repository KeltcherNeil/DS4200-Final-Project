import pandas as pd
import altair as alt

alt.renderers.enable("browser")


def main():
    data = pd.read_csv("ds4200_final_data_clean.csv")
    # drop nan values, drop (2024) labels from some GDP data
    data = data[data["Country GDP (millions USD)"] != "—N/a"]
    data["Country GDP (millions USD)"] = (data["Country GDP (millions USD)"].str.replace(
        r"\s*\(\d{4}\)", "", regex=True).str.replace(",", "", regex=False).astype(float))

    recent_data = data.loc[data.groupby("Country")["Year"].idxmax()]

    chart = alt.Chart(recent_data.sort_values("Country GDP (millions USD)", ascending=False).head(20)).mark_bar().encode(
        alt.X("Country", title="Country", sort=alt.SortField(field="Country GDP (millions USD)", order="descending")),
        alt.Y("Depressive Disorders", title="% with Depressive Disorders"),
    ).properties(
        title="% of Population with Depressive Disorders, Sorted by Top 20 Countries by GDP"
    )

    chart.show()


if __name__ == "__main__":
    main()
