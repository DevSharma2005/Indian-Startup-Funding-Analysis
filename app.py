from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load CSV
df = pd.read_csv("startup.csv")
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")


# Helper: format big numbers into human readable form
def format_amount(n):
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    elif n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    else:
        return str(n)

# Register as Jinja filter
app.jinja_env.filters['format_amount'] = format_amount

@app.route("/")
def home():
    total_funding = df["Amount in USD"].sum()
    total_startups = df["Startup Name"].nunique()
    total_investors = df["Investor Name"].nunique()
    avg_deal = df["Amount in USD"].mean()

    # Most funded industry
    top_industry = df.groupby("Industry Vertical")["Amount in USD"].sum().idxmax()

    # Top funded startup
    top_startup = df.groupby("Startup Name")["Amount in USD"].sum().idxmax()

    # Year with maximum funding
    df["Year"] = pd.to_datetime(df["Date"], errors="coerce").dt.year
    max_year = df.groupby("Year")["Amount in USD"].sum().idxmax()

    # Funding trend data
    funding_trends = df.groupby("Date")["Amount in USD"].sum().reset_index().sort_values("Date")

    return render_template("index.html",
                           total_funding=total_funding,
                           total_startups=total_startups,
                           total_investors=total_investors,
                           avg_deal=avg_deal,
                           top_industry=top_industry,
                           top_startup=top_startup,
                           max_year=max_year,
                           funding_trends=funding_trends.to_dict(orient="records"))

@app.route("/dashboard")
def dashboard():
    # Funding trend across years
    df["Year"] = df["Date"].dt.year
    funding_trends = (
        df.groupby("Year")["Amount in USD"]
          .sum()
          .reset_index()
          .sort_values("Year")
    )

    top_industries = df.groupby("Industry Vertical")["Amount in USD"].sum().nlargest(5).reset_index()
    top_cities = df.groupby("City")["Amount in USD"].sum().nlargest(5).reset_index()
    top_investors = df.groupby("Investor Name")["Amount in USD"].sum().nlargest(5).reset_index()

    total_funding = df["Amount in USD"].sum()
    total_startups = df["Startup Name"].nunique()
    total_investors = df["Investor Name"].nunique()
    avg_deal = df["Amount in USD"].mean()

    return render_template("dashboard.html",
                           funding_trends=funding_trends.to_dict(orient="records"),
                           top_industries=top_industries.to_dict(orient="records"),
                           top_cities=top_cities.to_dict(orient="records"),
                           top_investors=top_investors.to_dict(orient="records"),
                           total_funding=total_funding,
                           total_startups=total_startups,
                           total_investors=total_investors,
                           avg_deal=avg_deal
    )
    
@app.route('/filter', methods=['GET', 'POST'])
def filter_page():
    df_copy = df.copy()
    df_copy["Date"] = pd.to_datetime(df_copy["Date"], errors="coerce").dt.strftime("%Y-%m-%d")

    if request.method == 'POST':
        startup = request.form.get('startup')
        city = request.form.get('city')
        investor = request.form.get('investor')
        industry = request.form.get('industry')

        if startup:
            df_copy = df_copy[df_copy['Startup Name'].str.contains(startup, case=False)]
        if city:
            df_copy = df_copy[df_copy['City'].str.contains(city, case=False)]
        if investor:
            df_copy = df_copy[df_copy['Investor Name'].str.contains(investor, case=False)]
        if industry:
            df_copy = df_copy[df_copy['Industry Vertical'].str.contains(industry, case=False)]

    results = df_copy.to_dict(orient='records')
    return render_template("filter.html", startups=results)


if __name__ == "__main__":
    app.run(debug=True)
