import * as dotenv from "dotenv";
dotenv.config();
export class DeployConstant {

    public static readonly GLUE_JOB_NAME = process.env.GLUE_JOB_NAME ??''

    public static readonly GLUE_DISCORD_JOB_NAME = process.env.GLUE_DISCORD_JOB_NAME ??''

    public static readonly GLUE_SUMMARIZE_JOB_NAME = process.env.GLUE_SUMMARIZE_JOB_NAME ??''

    public static readonly GLUE_DISCORD_1CLICK_JOB_NAME = 'discord-1click-job'

    public static readonly GLUE_APPSTORE_JOB_NAME = 'appstore-job'

    public static readonly LLM_ANALYSIS_TEXT_TABLE_NAME = process.env.LLM_ANALYSIS_TEXT_TABLE_NAME ??''

    public static readonly DISCORD_SECRET_NAME = process.env.DISCORD_SECRET_NAME ??''

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

    public static readonly GLUE_APPSTORE_SUMMARY_TABLE = 'appstore_summary_result'

    public static readonly USER_JOBS_TABLE = 'user_jobs'

    public static readonly DDB_WEBHOOK_SETTINGS_TABLE = process.env.DDB_WEBHOOK_SETTINGS_TABLE??'webhook-settings'

    public static readonly DDB_CATEGORY_SETTINGS_TABLE = process.env.DDB_CATEGORY_SETTINGS_TABLE??'category-settings'

    public static readonly DDB_USER_JOBS_TABLE = process.env.DDB_USER_JOBS_TABLE??'user-jobs'

    private constructor() {}
}
