from app.database.db_collections import predictions_collection


class PredictionHistoryService:

    def get_predictions(self):
        predictions = predictions_collection.find({}).sort(
            "_id", -1
        )

        results = []

        for prediction in predictions:
            prediction.pop("_id", None)
            results.append(prediction)

        return results