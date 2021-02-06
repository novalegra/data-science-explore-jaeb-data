import pandas as pd
import utils
import equation_utils
from pumpsettings import PumpSettings


def run_equation_testing(input_file_name, jaeb_equations, traditional_equations):
    """
    Run equation testing, using the equations from an equation dict
    input_file_name: name of file, without extension
    jaeb_equations: PumpSettings object with equation data
    traditional_equations: PumpSettings object with equation data
    """

    data_path = utils.find_full_path(input_file_name, ".csv")
    df = pd.read_csv(data_path)
    result_cols = [
        "jaeb_aic",
        "traditional_aic",
        "jaeb_rmse",
        "traditional_rmse",
        "jaeb_sse",
        "traditional_sse",
        "jaeb_bic",
        "traditional_bic",
    ]
    output_df = pd.DataFrame(columns=result_cols)
    analysis_name = "evaluate-equations"

    # Keys for working with Jaeb exports
    tdd_key = "avg_total_insulin_per_day_outcomes"
    basal_key = "total_daily_scheduled_basal"  # Total daily basal
    carb_key = "avg_carbs_per_day_outcomes"  # Total daily CHO
    bmi_key = "BMI"
    bmi_percentile = "BMIPercentile"
    isf_key = "avg_isf"
    icr_key = "weighted_cir_outcomes"
    tir_key = "percent_70_180"
    age_key = "Age"

    """ Basal Analysis """
    df["jaeb_predicted_basals"] = df.apply(
        lambda x: jaeb_equations.basal_equation(x[tdd_key], x[carb_key]), axis=1
    )
    df["traditional_predicted_basals"] = df.apply(
        lambda x: traditional_equations.basal_equation(x[tdd_key]), axis=1
    )

    df["jaeb_basal_residual"] = df[basal_key] - df["jaeb_predicted_basals"]
    df["traditional_basal_residual"] = (
        df[basal_key] - df["traditional_predicted_basals"]
    )

    jaeb_basal_sum_squared_errors = sum(df["jaeb_basal_residual"] ** 2)
    traditional_basal_sum_squared_errors = sum(df["traditional_basal_residual"] ** 2)

    jaeb_basal_aic, jaeb_basal_bic = utils.aic_bic(
        df.shape[0], 2, jaeb_basal_sum_squared_errors, df["jaeb_basal_residual"].std()
    )
    traditional_basal_aic, traditional_basal_bic = utils.aic_bic(
        df.shape[0],
        1,
        traditional_basal_sum_squared_errors,
        df["traditional_basal_residual"].std(),
    )

    output_df.loc["Basal"] = [
        jaeb_basal_aic,
        traditional_basal_aic,
        (jaeb_basal_sum_squared_errors / df.shape[0]) ** 0.5,
        (traditional_basal_sum_squared_errors / df.shape[0]) ** 0.5,
        jaeb_basal_sum_squared_errors,
        traditional_basal_sum_squared_errors,
        jaeb_basal_bic,
        traditional_basal_bic,
    ]

    """ ISF Analysis """
    df["jaeb_predicted_isf"] = df.apply(
        lambda x: jaeb_equations.isf_equation(x[tdd_key], x[bmi_key]), axis=1
    )
    df["traditional_predicted_isf"] = df.apply(
        lambda x: traditional_equations.isf_equation(x[tdd_key]), axis=1
    )
    df = df.dropna(subset=["jaeb_predicted_isf", "traditional_predicted_isf"])

    df["jaeb_isf_residual"] = df[isf_key] - df["jaeb_predicted_isf"]
    df["traditional_isf_residual"] = df[isf_key] - df["traditional_predicted_isf"]

    jaeb_isf_sum_squared_errors = sum(df["jaeb_isf_residual"] ** 2)
    traditional_isf_sum_squared_errors = sum(df["traditional_isf_residual"] ** 2)

    jaeb_isf_aic, jaeb_isf_bic = utils.aic_bic(
        df.shape[0], 2, jaeb_isf_sum_squared_errors, df["jaeb_isf_residual"].std()
    )
    traditional_isf_aic, traditional_isf_bic = utils.aic_bic(
        df.shape[0],
        1,
        traditional_isf_sum_squared_errors,
        df["traditional_isf_residual"].std(),
    )

    output_df.loc["ISF"] = [
        jaeb_isf_aic,
        traditional_isf_aic,
        (jaeb_isf_sum_squared_errors / df.shape[0]) ** 0.5,
        (traditional_isf_sum_squared_errors / df.shape[0]) ** 0.5,
        jaeb_isf_sum_squared_errors,
        traditional_isf_sum_squared_errors,
        jaeb_isf_bic,
        traditional_isf_bic,
    ]

    """ ICR Analysis """
    df["jaeb_predicted_icr"] = df.apply(
        lambda x: jaeb_equations.icr_equation(x[tdd_key], x[carb_key]), axis=1
    )
    df["traditional_predicted_icr"] = df.apply(
        lambda x: traditional_equations.icr_equation(x[tdd_key]), axis=1
    )

    df["jaeb_icr_residual"] = df[icr_key] - df["jaeb_predicted_icr"]
    df["traditional_icr_residual"] = df[icr_key] - df["traditional_predicted_icr"]

    jaeb_icr_sum_squared_errors = sum(df["jaeb_icr_residual"] ** 2)
    traditional_icr_sum_squared_errors = sum(df["traditional_icr_residual"] ** 2)

    jaeb_icr_aic, jaeb_icr_bic = utils.aic_bic(
        df.shape[0], 2, jaeb_icr_sum_squared_errors, df["jaeb_icr_residual"].std()
    )
    traditional_icr_aic, traditional_icr_bic = utils.aic_bic(
        df.shape[0],
        1,
        traditional_icr_sum_squared_errors,
        df["traditional_icr_residual"].std(),
    )

    output_df.loc["ICR"] = [
        jaeb_icr_aic,
        traditional_icr_aic,
        (jaeb_icr_sum_squared_errors / df.shape[0]) ** 0.5,
        (traditional_icr_sum_squared_errors / df.shape[0]) ** 0.5,
        jaeb_icr_sum_squared_errors,
        traditional_icr_sum_squared_errors,
        jaeb_icr_bic,
        traditional_icr_bic,
    ]

    output_df["aic_dif"] = output_df["jaeb_aic"] - output_df["traditional_aic"]
    output_df["bic_dif"] = output_df["jaeb_bic"] - output_df["traditional_bic"]

    short_file_name = (
        input_file_name[0:10] if len(input_file_name) > 10 else input_file_name
    )
    output_df.to_csv(
        utils.get_save_path_with_file(
            input_file_name,
            analysis_name,
            short_file_name + "_equation_errors.csv",
            "data-analysis",
        )
    )

    df.to_csv(
        utils.get_save_path_with_file(
            input_file_name,
            analysis_name,
            short_file_name + "_with_equation_predictions.csv",
            "data-analysis",
        )
    )


# if __name__ == "__main__":
#     jaeb = PumpSettings(
#         equation_utils.jaeb_basal_equation,
#         equation_utils.jaeb_isf_equation,
#         equation_utils.jaeb_icr_equation,
#     )

#     traditional = PumpSettings(
#         equation_utils.traditional_basal_equation,
#         equation_utils.traditional_isf_equation,
#         equation_utils.traditional_icr_equation,
#     )

#     run_equation_testing(
#         "test_1_adult_aspirational_2020_10_11_01-v0_1-1635e10", jaeb, traditional
#     )

