import unittest
import pandas as pd
from rdkit.ML.Scoring import Scoring


def enrichment_factor(scores, labels, fractions):
    df = pd.DataFrame({"score": scores, "label": labels})
    temp_df = df.sort_values("score", ascending=False).reset_index()
    return Scoring.CalcEnrichment([[aLabel] for aLabel in temp_df["label"]], 0, fractions)


#-----------------

class test_enrichment_factor(unittest.TestCase):
    """test class of enrichment_factor
    """

    def test_ef_normal1(self):
        scores = [1, 2, 3, 4, 5]
        labels = [False, False, False, False, True]
        fractions = [0.2, 0.6]
        expected = [5, 5 / 3.0]
        actual = enrichment_factor(scores, labels, fractions)

        for i in range(len(expected)):
            self.assertAlmostEqual(expected[i], actual[i])


if __name__ == "__main__":
    unittest.main()
