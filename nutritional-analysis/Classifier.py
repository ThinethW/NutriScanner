"""
Food Classification Model for Sri Lankan Traditional Foods
Complete implementation with training, evaluation, and prediction
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_recall_fscore_support
)
from sklearn.preprocessing import LabelEncoder
import joblib
import json
import warnings

warnings.filterwarnings('ignore')

# Set style for better visualizations
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)


# ============================================================
# STEP 1: LOAD AND PREPARE DATA
# ============================================================

def load_data(filepath='traditional_food_reduced.csv'):
    """Load the reduced dataset"""
    df = pd.read_csv(filepath)
    print("=" * 70)
    print("DATA LOADED SUCCESSFULLY")
    print("=" * 70)
    print(f"Total foods: {len(df)}")
    print(f"Total features: {len(df.columns)}")
    print(f"\nFood categories:")
    print(df['Category'].value_counts())
    return df


# ============================================================
# STEP 2: CREATE TARGET LABELS (HEALTH CATEGORIES)
# ============================================================

def create_health_labels(df):
    """
    Create health-based classification labels
    Priority order: High-Protein > Weight-Loss > High-Fiber >
                    Nutrient-Dense > Energy-Dense > Balanced
    """
    labels = []

    for _, row in df.iterrows():
        # Priority 1: Very High Protein (>50%)
        if row['Protein_pct'] > 50:
            labels.append('Very-High-Protein')

        # Priority 2: High Protein (>30%)
        elif row['is_high_protein'] == 1 and row['Protein_pct'] > 30:
            labels.append('High-Protein')

        # Priority 3: Weight Loss Friendly
        elif row['weight_loss_friendly'] == 1:
            labels.append('Weight-Loss-Friendly')

        # Priority 4: High Fiber
        elif row['Fiber_to_carb_ratio'] > 0.5:
            labels.append('High-Fiber')

        # Priority 5: Nutrient Dense
        elif row['quality_score'] > 5:
            labels.append('Nutrient-Dense')

        # Priority 6: Energy Dense (high calorie)
        elif row['Energy_density'] > 4.5:
            labels.append('Energy-Dense')

        # Default: Balanced
        else:
            labels.append('Balanced')

    return labels


def add_labels_to_dataset(df):
    """Add health category labels to dataset"""
    df['health_category'] = create_health_labels(df)

    print("\n" + "=" * 70)
    print("HEALTH CATEGORIES CREATED")
    print("=" * 70)
    print("\nDistribution of health categories:")
    print(df['health_category'].value_counts())

    # Show examples from each category
    print("\n" + "=" * 70)
    print("EXAMPLES FROM EACH CATEGORY")
    print("=" * 70)
    for category in df['health_category'].unique():
        examples = df[df['health_category'] == category]['Food item'].head(3).tolist()
        print(f"\n{category}:")
        for i, food in enumerate(examples, 1):
            print(f"  {i}. {food}")

    return df


# ============================================================
# STEP 3: FEATURE SELECTION FOR CLASSIFICATION
# ============================================================

def select_features(df):
    """
    Select the most relevant features for classification
    """
    # Features to use (excluding text and target columns)
    feature_columns = [
        # Percentage features
        'Protein_pct',
        'Carb_pct',

        # Absolute nutrients
        'Protein (g)',
        'Carbohydrates digestible (g)',
        'Total fiber (g)',

        # Ratio features
        'Fiber_to_carb_ratio',
        'Protein_to_fat_ratio',
        'Healthy_fat_ratio',

        # Composite features
        'Energy_density',
        'quality_score',
        'Total_macros',

        # Binary flags
        'is_high_protein',
        'muscle_building',
        'weight_loss_friendly'
    ]

    print("\n" + "=" * 70)
    print("SELECTED FEATURES FOR CLASSIFICATION")
    print("=" * 70)
    print(f"Total features: {len(feature_columns)}")
    for i, feature in enumerate(feature_columns, 1):
        print(f"{i:2d}. {feature}")

    return feature_columns


# ============================================================
# STEP 4: BUILD AND TRAIN CLASSIFIER
# ============================================================

class FoodClassifier:
    """
    Main classifier class for food categorization
    """

    def __init__(self, model_type='random_forest'):
        """
        Initialize classifier

        model_type: 'random_forest', 'gradient_boosting', or 'decision_tree'
        """
        self.model_type = model_type
        self.model = None
        self.feature_columns = None
        self.label_encoder = LabelEncoder()
        self.class_names = None
        self.feature_importance = None

    def prepare_data(self, df, feature_columns):
        """Prepare features and labels"""
        self.feature_columns = feature_columns

        # Features
        X = df[feature_columns].copy()

        # Handle any missing values
        X = X.fillna(0)

        # Labels
        y = df['health_category']

        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        self.class_names = self.label_encoder.classes_.tolist()

        return X, y_encoded, y

    def create_model(self):
        """Create the classification model"""
        if self.model_type == 'random_forest':
            model = RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=3,
                min_samples_leaf=2,
                random_state=42,
                class_weight='balanced',
                n_jobs=-1
            )

        elif self.model_type == 'gradient_boosting':
            model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )

        elif self.model_type == 'decision_tree':
            model = DecisionTreeClassifier(
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                class_weight='balanced'
            )

        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

        return model

    def train(self, df, feature_columns, test_size=0.2):
        """Train the classifier"""
        print("\n" + "=" * 70)
        print(f"TRAINING {self.model_type.upper().replace('_', ' ')} CLASSIFIER")
        print("=" * 70)

        # Prepare data
        X, y_encoded, y_original = self.prepare_data(df, feature_columns)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded,
            test_size=test_size,
            random_state=42,
            stratify=y_encoded
        )

        print(f"\nDataset split:")
        print(f"  Training samples: {len(X_train)}")
        print(f"  Test samples: {len(X_test)}")
        print(f"  Number of classes: {len(self.class_names)}")

        # Create and train model
        self.model = self.create_model()

        print(f"\nTraining model...")
        self.model.fit(X_train, y_train)
        print("✅ Training complete!")

        # Evaluate on test set
        print("\n" + "=" * 70)
        print("MODEL EVALUATION")
        print("=" * 70)

        # Predictions
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)

        # Accuracy
        train_accuracy = accuracy_score(y_train, y_pred_train)
        test_accuracy = accuracy_score(y_test, y_pred_test)

        print(f"\nAccuracy:")
        print(f"  Training: {train_accuracy:.2%}")
        print(f"  Testing:  {test_accuracy:.2%}")

        # Cross-validation
        print(f"\nCross-validation (5-fold):")
        cv_scores = cross_val_score(self.model, X, y_encoded, cv=5)
        print(f"  Mean CV Score: {cv_scores.mean():.2%} (+/- {cv_scores.std() * 2:.2%})")

        # Detailed classification report
        print("\n" + "-" * 70)
        print("CLASSIFICATION REPORT")
        print("-" * 70)
        print(classification_report(
            y_test,
            y_pred_test,
            target_names=self.class_names,
            digits=3
        ))

        # Feature importance (for tree-based models)
        if hasattr(self.model, 'feature_importances_'):
            self.feature_importance = pd.DataFrame({
                'feature': self.feature_columns,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)

            print("\n" + "-" * 70)
            print("TOP 10 MOST IMPORTANT FEATURES")
            print("-" * 70)
            for i, row in self.feature_importance.head(10).iterrows():
                print(f"  {row['feature']:30s} {row['importance']:.4f}")

        # Store test data for visualization
        self.X_test = X_test
        self.y_test = y_test
        self.y_pred_test = y_pred_test

        return {
            'train_accuracy': train_accuracy,
            'test_accuracy': test_accuracy,
            'cv_scores': cv_scores
        }

    def plot_confusion_matrix(self, save_path='confusion_matrix.png'):
        """Plot confusion matrix"""
        cm = confusion_matrix(self.y_test, self.y_pred_test)

        plt.figure(figsize=(12, 10))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=self.class_names,
            yticklabels=self.class_names,
            cbar_kws={'label': 'Count'}
        )
        plt.title(f'Confusion Matrix - {self.model_type.replace("_", " ").title()}',
                  fontsize=16, fontweight='bold')
        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\n✅ Confusion matrix saved: {save_path}")
        plt.close()

    def plot_feature_importance(self, top_n=15, save_path='feature_importance.png'):
        """Plot feature importance"""
        if self.feature_importance is None:
            print("Feature importance not available for this model")
            return

        plt.figure(figsize=(10, 8))
        top_features = self.feature_importance.head(top_n)

        plt.barh(range(len(top_features)), top_features['importance'])
        plt.yticks(range(len(top_features)), top_features['feature'])
        plt.xlabel('Importance Score', fontsize=12)
        plt.title(f'Top {top_n} Most Important Features', fontsize=16, fontweight='bold')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Feature importance plot saved: {save_path}")
        plt.close()

    def plot_class_distribution(self, y_true, y_pred, save_path='class_distribution.png'):
        """Plot class distribution comparison"""
        true_counts = pd.Series(y_true).value_counts()
        pred_counts = pd.Series(y_pred).value_counts()

        # Convert to class names
        true_dist = {self.class_names[i]: true_counts.get(i, 0) for i in range(len(self.class_names))}
        pred_dist = {self.class_names[i]: pred_counts.get(i, 0) for i in range(len(self.class_names))}

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # True distribution
        ax1.bar(true_dist.keys(), true_dist.values(), color='steelblue')
        ax1.set_title('True Class Distribution', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Class')
        ax1.set_ylabel('Count')
        ax1.tick_params(axis='x', rotation=45)

        # Predicted distribution
        ax2.bar(pred_dist.keys(), pred_dist.values(), color='coral')
        ax2.set_title('Predicted Class Distribution', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Class')
        ax2.set_ylabel('Count')
        ax2.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Class distribution plot saved: {save_path}")
        plt.close()

    def predict(self, food_features):
        """
        Predict health category for new food

        food_features: dict with feature values
        """
        if self.model is None:
            raise ValueError("Model not trained yet!")

        # Create DataFrame with features
        X = pd.DataFrame([food_features])[self.feature_columns]
        X = X.fillna(0)

        # Predict
        prediction_encoded = self.model.predict(X)[0]
        prediction = self.label_encoder.inverse_transform([prediction_encoded])[0]

        # Get probabilities
        probabilities = self.model.predict_proba(X)[0]

        # Create probability dictionary
        prob_dict = {
            self.class_names[i]: float(probabilities[i])
            for i in range(len(self.class_names))
        }

        # Sort by probability
        prob_dict_sorted = dict(sorted(prob_dict.items(), key=lambda x: x[1], reverse=True))

        return {
            'predicted_category': prediction,
            'confidence': float(max(probabilities)),
            'probabilities': prob_dict_sorted
        }

    def save_model(self, filepath='food_classifier_model.pkl'):
        """Save trained model"""
        model_data = {
            'model': self.model,
            'model_type': self.model_type,
            'feature_columns': self.feature_columns,
            'label_encoder': self.label_encoder,
            'class_names': self.class_names,
            'feature_importance': self.feature_importance
        }

        joblib.dump(model_data, filepath)
        print(f"\n✅ Model saved: {filepath}")

    def load_model(self, filepath='food_classifier_model.pkl'):
        """Load trained model"""
        model_data = joblib.load(filepath)

        self.model = model_data['model']
        self.model_type = model_data['model_type']
        self.feature_columns = model_data['feature_columns']
        self.label_encoder = model_data['label_encoder']
        self.class_names = model_data['class_names']
        self.feature_importance = model_data.get('feature_importance')

        print(f"✅ Model loaded from: {filepath}")
        print(f"   Model type: {self.model_type}")
        print(f"   Classes: {len(self.class_names)}")


# ============================================================
# STEP 5: MAIN TRAINING PIPELINE
# ============================================================

def train_food_classifier(filepath='traditional_food_reduced.csv',
                          model_type='random_forest'):
    """
    Complete training pipeline
    """
    print("\n" + "=" * 70)
    print("FOOD CLASSIFICATION MODEL - TRAINING PIPELINE")
    print("=" * 70)

    # 1. Load data
    df = load_data(filepath)

    # 2. Create health labels
    df = add_labels_to_dataset(df)

    # 3. Select features
    feature_columns = select_features(df)

    # 4. Initialize and train classifier
    classifier = FoodClassifier(model_type=model_type)
    results = classifier.train(df, feature_columns)

    # 5. Create visualizations
    print("\n" + "=" * 70)
    print("CREATING VISUALIZATIONS")
    print("=" * 70)

    classifier.plot_confusion_matrix('confusion_matrix.png')
    classifier.plot_feature_importance(top_n=15, save_path='feature_importance.png')
    classifier.plot_class_distribution(
        classifier.y_test,
        classifier.y_pred_test,
        'class_distribution.png'
    )

    # 6. Save model
    classifier.save_model('food_classifier_model.pkl')

    # 7. Save labeled dataset
    output_path = 'foods_with_labels.csv'
    df.to_csv(output_path, index=False)
    print(f"✅ Labeled dataset saved: {output_path}")

    # 8. Save classification summary
    summary = {
        'model_type': model_type,
        'total_foods': len(df),
        'num_classes': len(classifier.class_names),
        'classes': classifier.class_names,
        'train_accuracy': float(results['train_accuracy']),
        'test_accuracy': float(results['test_accuracy']),
        'cv_mean': float(results['cv_scores'].mean()),
        'cv_std': float(results['cv_scores'].std()),
        'features_used': feature_columns
    }

    with open('classification_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✅ Classification summary saved: classification_summary.json")

    return classifier, df


# ============================================================
# STEP 6: PREDICTION EXAMPLES
# ============================================================

def test_predictions(classifier, df):
    """Test predictions on sample foods"""
    print("\n" + "=" * 70)
    print("TESTING PREDICTIONS ON SAMPLE FOODS")
    print("=" * 70)

    # Sample 5 random foods
    samples = df.sample(5, random_state=42)

    for idx, (_, row) in enumerate(samples.iterrows(), 1):
        print(f"\n{idx}. {row['Food item']}")
        print(f"   True category: {row['health_category']}")

        # Prepare features
        food_features = row[classifier.feature_columns].to_dict()

        # Predict
        result = classifier.predict(food_features)

        print(f"   Predicted: {result['predicted_category']}")
        print(f"   Confidence: {result['confidence']:.1%}")
        print(f"   Top 3 probabilities:")
        for cat, prob in list(result['probabilities'].items())[:3]:
            print(f"      {cat}: {prob:.1%}")


def predict_new_food_example(classifier):
    """Example: Predict category for a new food"""
    print("\n" + "=" * 70)
    print("EXAMPLE: PREDICTING NEW FOOD")
    print("=" * 70)

    # Example new food (high protein chicken)
    new_food = {
        'Protein_pct': 55.0,
        'Carb_pct': 10.0,
        'Protein (g)': 30.0,
        'Carbohydrates digestible (g)': 2.5,
        'Total fiber (g)': 0.5,
        'Fiber_to_carb_ratio': 0.2,
        'Protein_to_fat_ratio': 5.5,
        'Healthy_fat_ratio': 0.65,
        'Energy_density': 3.8,
        'quality_score': 7.5,
        'Total_macros': 38.0,
        'is_high_protein': 1,
        'muscle_building': 1,
        'weight_loss_friendly': 0
    }

    print("\nNew Food Features:")
    for key, value in new_food.items():
        print(f"  {key}: {value}")

    result = classifier.predict(new_food)

    print(f"\n📊 PREDICTION RESULTS:")
    print(f"   Category: {result['predicted_category']}")
    print(f"   Confidence: {result['confidence']:.1%}")
    print(f"\n   All probabilities:")
    for cat, prob in result['probabilities'].items():
        bar = '█' * int(prob * 30)
        print(f"      {cat:25s} {prob:6.1%} {bar}")


# ============================================================
# STEP 7: MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    # Train the classifier
    classifier, df_labeled = train_food_classifier(
        filepath='traditional_food_reduced.csv',
        model_type='random_forest'  # Options: 'random_forest', 'gradient_boosting', 'decision_tree'
    )

    # Test predictions on existing foods
    test_predictions(classifier, df_labeled)

    # Predict for new food
    predict_new_food_example(classifier)

    print("\n" + "=" * 70)
    print("✅ CLASSIFICATION MODEL COMPLETE!")
    print("=" * 70)
    print("\nFiles created:")
    print("  1. food_classifier_model.pkl - Trained model")
    print("  2. foods_with_labels.csv - Dataset with predicted categories")
    print("  3. confusion_matrix.png - Model performance visualization")
    print("  4. feature_importance.png - Feature ranking")
    print("  5. class_distribution.png - Class balance")
    print("  6. classification_summary.json - Model metadata")
    print("\nNext steps:")
    print("  - Review confusion matrix for model performance")
    print("  - Check feature importance to understand key predictors")
    print("  - Use saved model for real-time predictions")
    print("  - Integrate with recommendation engine")