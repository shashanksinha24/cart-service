from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

user_carts = [
    {
        "user_id": 1, 
        "products": [
            {"id": 1, "quantity": 100},
            {"id": 2, "quantity": 200},
        ]
    },
    {
        "user_id": 2, 
        "products": [
            {"id": 4, "quantity": 25},
            {"id": 5, "quantity": 75},
            {"id": 6, "quantity": 100},
        ]
    }
]

PRODUCT_SERVICE_URL = "product-service-ckui.onrender.com/products"

@app.route("/carts/<int:user_id>", methods=['GET'])
def get_cart_by_user_id(user_id):
    cart = next((u['products'] for u in user_carts if u['user_id'] == user_id), None)

    cart_with_products = []
    total_price = 0.0

    if cart is None or len(cart) == 0:
        return jsonify({"message": "Cart is empty or does not exist"}), 200

    for product in cart:
        product_id = product["id"]
        product_response = requests.get(f"{PRODUCT_SERVICE_URL}/{product_id}")

        if product_response.status_code == 200:
            product_data = product_response.json()
            product_data["quantity"] = product["quantity"]
            product_price = product_data["price"]
            total_product_price = product_price * product["quantity"]
            total_price += total_product_price

            cart_with_products.append(
                {
                    "name": product_data["name"],
                    "price": product_price,
                    "quantity": product["quantity"],
                    "total_product_price": total_product_price
                }
            )
        else:
            return jsonify({"message": "Product not found"}), 404

    return jsonify({
        "user_id": user_id,
        "cart": cart_with_products,
        "total_price": total_price
    })

@app.route("/carts/<int:user_id>/add/<int:product_id>", methods=['POST'])
def add_product_to_cart(user_id, product_id):
    cart_details = request.get_json()
    quantity = cart_details.get("quantity")

    product_response = requests.get(f"{PRODUCT_SERVICE_URL}/{product_id}")

    if product_response.status_code == 200:
        product_data = product_response.json()

        user_cart = next((u for u in user_carts if u['user_id'] == user_id), None)

        if user_cart:
            products = next((u['products'] for u in user_carts if u['user_id'] == user_id), None)

            if products:
                for p in products:
                    if p["id"] == product_id:
                        p["quantity"] += quantity
                        return jsonify({"message": "Product quantity has been updated"}), 201
            else:
                user_carts["products"].append({"id": product_id, "quantity": quantity})
        else:
            user_carts.append({"user_id": user_id, "products": [{"id": product_id, "quantity": quantity}]})
            return jsonify({"message": "Product has been added to the cart"}), 201
    else:
        return jsonify({"message": "Product not found"}), 404


@app.route("/carts/<int:user_id>/remove/<int:product_id>", methods=['POST'])
def remove_product_from_cart(user_id, product_id):
    cart_details = request.get_json()
    quantity = cart_details.get("quantity")

    user_cart = next((u for u in user_carts if u['user_id'] == user_id), None)
    product_response = requests.get(f"{PRODUCT_SERVICE_URL}/{product_id}")

    if product_response.status_code == 200:
        product_data = product_response.json()

        if user_cart:
            products = next((u['products'] for u in user_carts if u['user_id'] == user_id), None)

            if products:
                for p in products:
                    if p["id"] == product_id:
                        if p["quantity"] > quantity:
                            p["quantity"] -= quantity
                            return jsonify({"message": "Product quantity has been updated"}), 201
                        else:
                            products.remove(p)
                            return jsonify({"message": "Product has been removed from the cart"}), 201
            else:
                return jsonify({"message": "Product not found in the cart"}), 404
        else:
            return jsonify({"message": "User cart not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)
