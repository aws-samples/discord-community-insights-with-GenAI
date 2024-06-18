import * as dotenv from "dotenv";
dotenv.config();
export class DeployConstant {

    public static readonly GLUE_JOB_NAME = process.env.GLUE_JOB_NAME ??''

    public static readonly GLUE_DISCORD_JOB_NAME = process.env.GLUE_DISCORD_JOB_NAME ??''

    public static readonly GLUE_SUMMARIZE_JOB_NAME = process.env.GLUE_SUMMARIZE_JOB_NAME ??''

    public static readonly LLM_ANALYSIS_TEXT_TABLE_NAME = process.env.LLM_ANALYSIS_TEXT_TABLE_NAME ??''

    /**
     * please modify the bucket name
     */

    public static readonly S3_BUCKET_NAME = process.env.S3_BUCKET_NAME??''

    public static readonly RAW_DATA_PREFIX = process.env.RAW_DATA_PREFIX??''

    /**
     *
     * @private
     */
    public static readonly GLUE_DATABASE = process.env.GLUE_DATABASE??''

    public static readonly GLUE_TABLE = process.env.GLUE_TABLE??''
    
    public static readonly GLUE_SUMMARY_TABLE = process.env.GLUE_SUMMARY_TABLE??''

    private constructor() {}
}
