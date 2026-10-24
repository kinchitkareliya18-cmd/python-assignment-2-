
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# File paths
BASE_DIR = Path(__file__).parent
CSV_FILE = BASE_DIR / "Q10_sales_data.csv"
OUTPUT_FILE = BASE_DIR / "sales_dashboard.png"

def main():
    try:
        df = pd.read_csv(CSV_FILE)

        required_columns = {"Product", "Category", "Sales"}
        if not required_columns.issubset(df.columns):
            print("CSV must contain Product, Category, and Sales columns.")
            return

        df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
        df = df.dropna(subset=["Product", "Category", "Sales"])

        if df.empty:
            print("No valid sales data found.")
            return

        total_sales = df["Sales"].sum()
        average_sales = df["Sales"].mean()
        top_product = df.groupby("Product")["Sales"].sum().idxmax()

        print("\n===== SALES DASHBOARD SUMMARY =====")
        print(f"Total Sales:   {total_sales:.2f}")
        print(f"Average Sale:  {average_sales:.2f}")
        print(f"Top Product:   {top_product}")
        print(f"Records:       {len(df)}")

        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        fig.suptitle("Sales Data Visualization Dashboard",
                     fontsize=16, fontweight="bold")

        # Chart 1: Sales by product
        product_sales = df.groupby("Product")["Sales"].sum().sort_values()
        product_sales.plot(kind="bar", ax=axes[0], title="Sales by Product")
        axes[0].set_ylabel("Sales")
        axes[0].tick_params(axis="x", rotation=45)

        # Chart 2: Sales by category
        category_sales = df.groupby("Category")["Sales"].sum()
        category_sales.plot(
            kind="pie", autopct="%1.1f%%", ax=axes[1],
            title="Sales by Category"
        )
        axes[1].set_ylabel("")

        # Chart 3: Sales distribution
        axes[2].hist(df["Sales"], bins=5, edgecolor="black")
        axes[2].set_title("Sales Distribution")
        axes[2].set_xlabel("Sales Amount")
        axes[2].set_ylabel("Frequency")

        plt.tight_layout()
        plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
        print(f"\nDashboard exported to: {OUTPUT_FILE}")

        plt.show()

    except FileNotFoundError:
        print(f"CSV file not found: {CSV_FILE}")
    except Exception as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()
