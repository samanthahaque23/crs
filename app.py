from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd
from sklearn.metrics.pairwise import linear_kernel

# Load the recommendation system from the pickle file
with open('recommendation_system.pkl', 'rb') as f:
    data = pickle.load(f)

# Load the top-loved products with images
with open('top_loved_with_images.pkl', 'rb') as f:
    top_loved_df = pickle.load(f)

# Extract data from the pickle
tfidf = data['tfidf']
cosine_sim = data['cosine_sim']
product_df = data['product_df']
tfidf_matrix = data['tfidf_matrix']

# Initialize Flask app
app = Flask(__name__)

# Home page displaying top-loved products
@app.route('/')
def index():
    # Assuming the first 10 top-loved products
    top_loved_products = top_loved_df.head(10)

    # Return top-loved product details
    return render_template('index.html',
                           top_loved_products=top_loved_df[['product_name', 'image_link', 'brand_name', 'price_usd', 'loves_count']].to_dict(orient='records'))


# API route to serve top-loved products as JSON
@app.route('/api/top_loved_products', methods=['GET'])
def get_top_loved_products():
    # Get top 10 top-loved products
    top_loved_products = top_loved_df.head(10)

    # Return the top-loved products as JSON
    return jsonify(top_loved_products[['product_name', 'image_link', 'brand_name', 'price_usd', 'loves_count']].to_dict(orient='records'))


# Page for product recommendations (HTML form)
@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')


# Handle product recommendations based on user input and display in HTML
@app.route('/recommend_products', methods=['POST'])
def recommend_products():
    product_name = request.form.get('product_name')
    skin_type = request.form.get('skin_type')
    secondary_category = request.form.get('secondary_category')

    if product_name:
        result = get_recommendations_by_product_name(product_name)
    elif skin_type and secondary_category:
        result = get_recommendations_by_skin_and_category(skin_type, secondary_category)
    else:
        return render_template('recommend.html', data=[], error="Please provide either a product name or both skin type and category.")

    return render_template('recommend.html', data=result)


# API endpoint for recommendations (returns JSON)
@app.route('/api/recommend_products', methods=['POST'])
def api_recommend_products():
    data = request.get_json()
    product_name = data.get('product_name')
    skin_type = data.get('skin_type')
    secondary_category = data.get('secondary_category')

    if product_name:
        result = get_recommendations_by_product_name(product_name)
    elif skin_type and secondary_category:
        result = get_recommendations_by_skin_and_category(skin_type, secondary_category)
    else:
        return jsonify({"error": "Please provide either a product name or both skin type and category."}), 400

    return jsonify({"recommendations": result})


# Recommendation based on product name
def get_recommendations_by_product_name(product_name):
    if product_name not in product_df['product_name'].values:
        return []

    idx = product_df[product_df['product_name'] == product_name].index[0]
    similarity_scores = cosine_sim[idx]
    indices = similarity_scores.argsort()[-6:-1][::-1]

    # Include price_usd and brand_name in the response
    return product_df.iloc[indices][['product_name', 'ingredients', 'combined_skin_type', 'brand_name', 'price_usd']].values.tolist()


# Recommendation based on skin type and category
def get_recommendations_by_skin_and_category(skin_type, secondary_category):
    input_features = f"{skin_type} {secondary_category}"
    input_tfidf = tfidf.transform([input_features])
    similarity_scores = linear_kernel(input_tfidf, tfidf_matrix)
    similarity_scores = similarity_scores.flatten()

    indices = similarity_scores.argsort()[-5:][::-1]

    # Include price_usd and brand_name in the response
    return product_df.iloc[indices][['product_name', 'ingredients', 'combined_skin_type', 'brand_name', 'price_usd']].values.tolist()


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
