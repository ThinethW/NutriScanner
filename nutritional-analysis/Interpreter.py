"""
Enhanced Nutrition Interpretation System for NutriScanner
Includes chronic disease-specific recommendations and meal scoring
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import json
from typing import Dict, List, Tuple
import warnings

warnings.filterwarnings('ignore')


class NutritionInterpreter:
    """
    Advanced nutrition interpretation system with chronic disease management
    """

    def __init__(self):
        self.classifier = None
        self.scaler = StandardScaler()
        self.feature_columns = None

        # Chronic disease thresholds (per serving ~150g)
        self.disease_limits = {
            'diabetes': {
                'carbs_max': 45,  # grams
                'sugar_max': 10,
                'fiber_min': 3,
                'gi_preference': 'low'  # low glycemic index
            },
            'hypertension': {
                'sodium_max': 500,  # mg
                'potassium_min': 400,
                'fat_max': 10
            },
            'heart_disease': {
                'saturated_fat_max': 3,  # grams
                'cholesterol_max': 50,  # mg
                'fiber_min': 4,
                'omega3_preferred': True
            },
            'kidney_disease': {
                'protein_max': 15,  # grams
                'sodium_max': 400,
                'potassium_max': 500,
                'phosphorus_max': 200
            },
            'high_cholesterol': {
                'saturated_fat_max': 3,
                'trans_fat_max': 0.5,
                'dietary_fiber_min': 5
            }
        }

    def load_model(self, model_path='food_classifier_model.pkl'):
        """Load pre-trained classification model"""
        try:
            model_data = joblib.load(model_path)
            self.classifier = model_data['model']
            self.feature_columns = model_data['feature_columns']
            print(f"✅ Model loaded successfully")
            return True
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False

    def calculate_health_score(self, nutrition_data: Dict,
                               chronic_diseases: List[str] = None) -> Dict:
        """
        Calculate comprehensive health score (0-100) based on nutrition
        and user's chronic diseases

        Args:
            nutrition_data: Dict with nutritional values
            chronic_diseases: List of user's conditions

        Returns:
            Dict with score, breakdown, and recommendations
        """

        if chronic_diseases is None:
            chronic_diseases = []

        # Base nutritional quality score (0-100)
        base_score = self._calculate_base_nutrition_score(nutrition_data)

        # Disease-specific penalties
        disease_penalties = 0
        warnings = []

        for disease in chronic_diseases:
            penalty, disease_warnings = self._check_disease_compliance(
                nutrition_data, disease
            )
            disease_penalties += penalty
            warnings.extend(disease_warnings)

        # Final score (cannot go below 0)
        final_score = max(0, base_score - disease_penalties)

        # Categorize score
        if final_score >= 80:
            rating = "Excellent"
            color = "green"
        elif final_score >= 60:
            rating = "Good"
            color = "light-green"
        elif final_score >= 40:
            rating = "Fair"
            color = "yellow"
        else:
            rating = "Poor"
            color = "red"

        return {
            'overall_score': round(final_score, 1),
            'base_score': round(base_score, 1),
            'disease_penalty': round(disease_penalties, 1),
            'rating': rating,
            'color': color,
            'warnings': warnings,
            'breakdown': self._score_breakdown(nutrition_data)
        }

    def _calculate_base_nutrition_score(self, nutrition_data: Dict) -> float:
        """Calculate base nutrition quality score"""
        score = 50  # Start at neutral

        # Protein quality (+0 to +15 points)
        protein_pct = nutrition_data.get('Protein_pct', 0)
        if protein_pct >= 30:
            score += 15
        elif protein_pct >= 20:
            score += 10
        elif protein_pct >= 15:
            score += 5

        # Fiber content (+0 to +15 points)
        fiber = nutrition_data.get('Total fiber (g)', 0)
        if fiber >= 5:
            score += 15
        elif fiber >= 3:
            score += 10
        elif fiber >= 2:
            score += 5

        # Fat quality (+0 to +10 points)
        healthy_fat_ratio = nutrition_data.get('Healthy_fat_ratio', 0)
        if healthy_fat_ratio >= 0.7:
            score += 10
        elif healthy_fat_ratio >= 0.5:
            score += 6
        elif healthy_fat_ratio >= 0.3:
            score += 3

        # Calorie density (-0 to +10 points)
        energy_density = nutrition_data.get('Energy_density', 0)
        if energy_density <= 2:  # Low calorie density
            score += 10
        elif energy_density <= 4:
            score += 5
        elif energy_density > 6:  # High calorie density
            score -= 5

        # Nutrient density (+0 to +10 points)
        nutrient_density = nutrition_data.get('Nutrient_density_score', 0)
        if nutrient_density >= 8:
            score += 10
        elif nutrient_density >= 5:
            score += 5

        return min(100, max(0, score))

    def _check_disease_compliance(self, nutrition_data: Dict,
                                  disease: str) -> Tuple[float, List[str]]:
        """
        Check if nutrition complies with disease requirements
        Returns penalty points and warnings
        """
        disease = disease.lower()

        if disease not in self.disease_limits:
            return 0, []

        limits = self.disease_limits[disease]
        penalty = 0
        warnings = []

        # Check each limit
        if disease == 'diabetes':
            carbs = nutrition_data.get('Carbohydrates digestible (g)', 0)
            if carbs > limits['carbs_max']:
                excess = carbs - limits['carbs_max']
                penalty += min(20, excess * 0.5)
                warnings.append({
                    'type': 'critical',
                    'message': f'High carbohydrates: {carbs:.1f}g (limit: {limits["carbs_max"]}g)',
                    'suggestion': 'Consider reducing rice portion or choosing red rice'
                })

            fiber = nutrition_data.get('Total fiber (g)', 0)
            if fiber < limits['fiber_min']:
                penalty += 10
                warnings.append({
                    'type': 'warning',
                    'message': f'Low fiber: {fiber:.1f}g (need: >{limits["fiber_min"]}g)',
                    'suggestion': 'Add more vegetables and switch to brown/red rice'
                })

        elif disease == 'hypertension':
            # Sodium check (estimated from typical Sri Lankan recipes)
            fat = nutrition_data.get('Fat (g)', 0)
            if fat > limits['fat_max']:
                penalty += 15
                warnings.append({
                    'type': 'critical',
                    'message': f'High fat content: {fat:.1f}g',
                    'suggestion': 'Avoid coconut milk-based curries and fried items'
                })

        elif disease == 'heart_disease':
            sfa = nutrition_data.get('SFA', 0)
            if sfa > limits['saturated_fat_max']:
                excess = sfa - limits['saturated_fat_max']
                penalty += min(25, excess * 3)
                warnings.append({
                    'type': 'critical',
                    'message': f'High saturated fat: {sfa:.1f}g (limit: {limits["saturated_fat_max"]}g)',
                    'suggestion': 'Limit coconut-based curries and choose lean proteins'
                })

        elif disease == 'kidney_disease':
            protein = nutrition_data.get('Protein (g)', 0)
            if protein > limits['protein_max']:
                excess = protein - limits['protein_max']
                penalty += min(20, excess * 2)
                warnings.append({
                    'type': 'critical',
                    'message': f'High protein: {protein:.1f}g (limit: {limits["protein_max"]}g)',
                    'suggestion': 'Reduce meat/fish portion, increase vegetables'
                })

        elif disease == 'high_cholesterol':
            sfa = nutrition_data.get('SFA', 0)
            if sfa > limits['saturated_fat_max']:
                penalty += 15
                warnings.append({
                    'type': 'warning',
                    'message': f'Saturated fat: {sfa:.1f}g exceeds limit',
                    'suggestion': 'Choose fish over meat, limit coconut products'
                })

        return penalty, warnings

    def _score_breakdown(self, nutrition_data: Dict) -> Dict:
        """Provide detailed breakdown of score components"""
        return {
            'protein_quality': self._rate_component(
                nutrition_data.get('Protein_pct', 0),
                thresholds=[15, 20, 30],
                labels=['Low', 'Moderate', 'Good', 'Excellent']
            ),
            'fiber_content': self._rate_component(
                nutrition_data.get('Total fiber (g)', 0),
                thresholds=[2, 3, 5],
                labels=['Low', 'Moderate', 'Good', 'Excellent']
            ),
            'fat_quality': self._rate_component(
                nutrition_data.get('Healthy_fat_ratio', 0),
                thresholds=[0.3, 0.5, 0.7],
                labels=['Poor', 'Fair', 'Good', 'Excellent']
            ),
            'calorie_density': self._rate_component(
                nutrition_data.get('Energy_density', 0),
                thresholds=[4, 6, 8],
                labels=['Excellent', 'Good', 'Moderate', 'High'],
                reverse=True
            )
        }

    def _rate_component(self, value: float, thresholds: List[float],
                        labels: List[str], reverse: bool = False) -> str:
        """Rate a single component based on thresholds"""
        if reverse:
            for i, threshold in enumerate(thresholds):
                if value <= threshold:
                    return labels[i]
            return labels[-1]
        else:
            for i, threshold in enumerate(thresholds):
                if value < threshold:
                    return labels[i]
            return labels[-1]

    def get_meal_recommendations(self, detected_foods: List[Dict],
                                 chronic_diseases: List[str]) -> Dict:
        """
        Analyze complete meal and provide recommendations

        Args:
            detected_foods: List of detected food items with nutrition
            chronic_diseases: User's health conditions

        Returns:
            Comprehensive meal analysis and recommendations
        """

        # Aggregate nutrition from all foods
        total_nutrition = self._aggregate_nutrition(detected_foods)

        # Calculate health score
        health_analysis = self.calculate_health_score(
            total_nutrition,
            chronic_diseases
        )

        # Generate specific recommendations
        recommendations = self._generate_recommendations(
            detected_foods,
            total_nutrition,
            chronic_diseases,
            health_analysis
        )

        # Find healthier alternatives
        alternatives = self._suggest_alternatives(
            detected_foods,
            chronic_diseases
        )

        return {
            'total_nutrition': total_nutrition,
            'health_score': health_analysis,
            'recommendations': recommendations,
            'alternatives': alternatives,
            'detected_items': detected_foods
        }

    def _aggregate_nutrition(self, detected_foods: List[Dict]) -> Dict:
        """Sum up nutrition from all detected foods"""
        total = {
            'Energy (kcal)': 0,
            'Protein (g)': 0,
            'Carbohydrates digestible (g)': 0,
            'Fat (g)': 0,
            'Total fiber (g)': 0,
            'SFA': 0,
            'MUFA': 0,
            'PUFA': 0
        }

        for food in detected_foods:
            nutrition = food.get('nutrition', {})
            for key in total.keys():
                total[key] += nutrition.get(key, 0)

        # Calculate derived metrics
        total_calories = total['Energy (kcal)']
        if total_calories > 0:
            total['Protein_pct'] = (total['Protein (g)'] * 4 / total_calories) * 100
            total['Carb_pct'] = (total['Carbohydrates digestible (g)'] * 4 / total_calories) * 100
            total['Fat_pct'] = (total['Fat (g)'] * 9 / total_calories) * 100
            total['Healthy_fat_ratio'] = (total['MUFA'] + total['PUFA']) / (total['Fat (g)'] + 0.1)
            total['Fiber_to_carb_ratio'] = total['Total fiber (g)'] / (total['Carbohydrates digestible (g)'] + 0.1)
            total['Energy_density'] = total_calories / 100
            total['Nutrient_density_score'] = (total['Protein (g)'] + total['Total fiber (g)']) / (total_calories / 100)

        return total

    def _generate_recommendations(self, detected_foods: List[Dict],
                                  total_nutrition: Dict,
                                  chronic_diseases: List[str],
                                  health_analysis: Dict) -> Dict:
        """Generate actionable recommendations"""

        positive = []  # What's good
        caution = []  # What to watch
        avoid = []  # What to reduce/avoid

        # Check warnings from health analysis
        for warning in health_analysis.get('warnings', []):
            if warning['type'] == 'critical':
                avoid.append(warning)
            else:
                caution.append(warning)

        # Add positive feedback
        if health_analysis['overall_score'] >= 70:
            positive.append({
                'message': 'Well-balanced meal overall',
                'detail': 'Good combination of nutrients'
            })

        if total_nutrition.get('Protein (g)', 0) >= 20:
            positive.append({
                'message': 'Excellent protein content',
                'detail': f"{total_nutrition['Protein (g)']:.1f}g protein supports muscle health"
            })

        if total_nutrition.get('Total fiber (g)', 0) >= 5:
            positive.append({
                'message': 'High fiber content',
                'detail': 'Helps with digestion and blood sugar control'
            })

        # Disease-specific recommendations
        if 'diabetes' in [d.lower() for d in chronic_diseases]:
            rice_found = any('rice' in food.get('name', '').lower()
                             for food in detected_foods)
            if rice_found:
                caution.append({
                    'message': 'White rice detected',
                    'suggestion': 'Consider switching to red/brown rice for better blood sugar control'
                })

        if 'heart_disease' in [d.lower() for d in chronic_diseases]:
            fried_found = any('fried' in food.get('name', '').lower()
                              for food in detected_foods)
            if fried_found:
                avoid.append({
                    'message': 'Fried items detected',
                    'suggestion': 'Choose grilled, steamed, or boiled alternatives'
                })

        return {
            'positive': positive[:3],  # Top 3
            'caution': caution[:3],
            'avoid': avoid[:2]
        }

    def _suggest_alternatives(self, detected_foods: List[Dict],
                              chronic_diseases: List[str]) -> List[Dict]:
        """Suggest healthier alternatives for detected foods"""

        alternatives = []

        # Common unhealthy foods and their alternatives
        substitutions = {
            'white rice': {
                'alternative': 'Red rice or brown rice',
                'benefit': 'Lower glycemic index, higher fiber',
                'conditions': ['diabetes', 'heart_disease']
            },
            'fried chicken': {
                'alternative': 'Grilled or curry chicken',
                'benefit': 'Lower saturated fat and calories',
                'conditions': ['heart_disease', 'high_cholesterol']
            },
            'coconut milk curry': {
                'alternative': 'Tomato-based or thin curry',
                'benefit': 'Much lower saturated fat',
                'conditions': ['heart_disease', 'high_cholesterol']
            },
            'fried fish': {
                'alternative': 'Fish ambulthiyal or grilled fish',
                'benefit': 'Preserves omega-3, less fat',
                'conditions': ['heart_disease']
            },
            'potato curry': {
                'alternative': 'Green bean or brinjal curry',
                'benefit': 'Lower carbs, higher fiber',
                'conditions': ['diabetes']
            }
        }

        # Check each detected food
        for food in detected_foods:
            food_name = food.get('name', '').lower()

            for unhealthy_food, sub_info in substitutions.items():
                if unhealthy_food in food_name:
                    # Check if relevant to user's conditions
                    relevant = not chronic_diseases or any(
                        d.lower() in sub_info['conditions']
                        for d in chronic_diseases
                    )

                    if relevant:
                        alternatives.append({
                            'current': food.get('name'),
                            'suggested': sub_info['alternative'],
                            'benefit': sub_info['benefit'],
                            'priority': 'high' if food_name in ['fried', 'white rice'] else 'medium'
                        })

        return alternatives[:3]  # Return top 3 most important


# Example usage function
def analyze_meal_example():
    """Example of how to use the NutritionInterpreter"""

    # Initialize interpreter
    interpreter = NutritionInterpreter()

    # Example: User scanned a meal
    detected_foods = [
        {
            'name': 'Boiled Rice, Nadu, White',
            'portion': 200,  # grams
            'confidence': 0.95,
            'nutrition': {
                'Energy (kcal)': 262.36,
                'Protein (g)': 5.56,
                'Carbohydrates digestible (g)': 57.42,
                'Fat (g)': 1.06,
                'Total fiber (g)': 1.76,
                'SFA': 0.36,
                'MUFA': 0.22,
                'PUFA': 0.32
            }
        },
        {
            'name': 'Chicken curry',
            'portion': 150,
            'confidence': 0.92,
            'nutrition': {
                'Energy (kcal)': 185.73,
                'Protein (g)': 22.94,
                'Carbohydrates digestible (g)': 4.55,
                'Fat (g)': 7.17,
                'Total fiber (g)': 2.57,
                'SFA': 3.96,
                'MUFA': 1.16,
                'PUFA': 0.77
            }
        },
        {
            'name': 'Dhal curry, thick',
            'portion': 100,
            'confidence': 0.88,
            'nutrition': {
                'Energy (kcal)': 129.43,
                'Protein (g)': 7.51,
                'Carbohydrates digestible (g)': 16.49,
                'Fat (g)': 2.36,
                'Total fiber (g)': 3.93,
                'SFA': 1.64,
                'MUFA': 0.34,
                'PUFA': 0.30
            }
        }
    ]

    # User's chronic diseases
    user_diseases = ['diabetes', 'hypertension']

    # Analyze meal
    analysis = interpreter.get_meal_recommendations(
        detected_foods,
        user_diseases
    )

    # Print results
    print("=" * 70)
    print("MEAL ANALYSIS RESULTS")
    print("=" * 70)

    print(f"\n🍽️  Detected Items: {len(detected_foods)}")
    for food in detected_foods:
        print(f"   • {food['name']} ({food['portion']}g) - {food['confidence']:.0%} confidence")

    print(f"\n📊 Total Nutrition:")
    nutrition = analysis['total_nutrition']
    print(f"   Calories: {nutrition['Energy (kcal)']:.0f} kcal")
    print(f"   Protein: {nutrition['Protein (g)']:.1f}g ({nutrition.get('Protein_pct', 0):.1f}%)")
    print(f"   Carbs: {nutrition['Carbohydrates digestible (g)']:.1f}g ({nutrition.get('Carb_pct', 0):.1f}%)")
    print(f"   Fat: {nutrition['Fat (g)']:.1f}g ({nutrition.get('Fat_pct', 0):.1f}%)")
    print(f"   Fiber: {nutrition['Total fiber (g)']:.1f}g")

    health = analysis['health_score']
    print(f"\n💯 Health Score: {health['overall_score']}/100 ({health['rating']})")
    print(f"   Base Score: {health['base_score']:.1f}")
    print(f"   Disease Penalty: -{health['disease_penalty']:.1f}")

    print(f"\n✅ What's Good:")
    for item in analysis['recommendations']['positive']:
        print(f"   • {item['message']}")
        print(f"     → {item['detail']}")

    print(f"\n⚠️  Caution:")
    for item in analysis['recommendations']['caution']:
        print(f"   • {item.get('message', item.get('suggestion'))}")

    print(f"\n❌ Avoid/Reduce:")
    for item in analysis['recommendations']['avoid']:
        print(f"   • {item.get('message', item.get('suggestion'))}")

    if analysis['alternatives']:
        print(f"\n🔄 Healthier Alternatives:")
        for alt in analysis['alternatives']:
            print(f"   Instead of: {alt['current']}")
            print(f"   Try: {alt['suggested']}")
            print(f"   Why: {alt['benefit']}\n")


if __name__ == "__main__":
    analyze_meal_example()