class Incident:
    def __init__(self, product: str, status_message: str, timestamp: str):
        self.product = product
        self.status_message = status_message
        self.timestamp = timestamp

    def __repr__(self):
        return f"Incident(product={self.product}, status_message={self.status_message}, timestamp={self.timestamp})"

    def to_dict(self):
        return {
            "product": self.product,
            "status_message": self.status_message,
            "timestamp": self.timestamp
        }