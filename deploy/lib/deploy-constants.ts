export class DeployConstant {

    public static readonly GLUE_JOB_NAME = 'llm-analysis-text-job'

    public static readonly LLM_ANALYSIS_TEXT_TABLE_NAME = 'prompt-template'

    /**
     * please modify the bucket name
     */
    public static readonly S3_BUCKET_NAME = 'llm-analysis-text-998'

    public static readonly RAW_DATA_PREFIX = 'raw-data/'

    /**
     *
     * @private
     */
    public static readonly GLUE_DATABASE = 'llm_text_db'

    public static readonly GLUE_TABLE = 'sentiment_result'

    private constructor() {}
}
