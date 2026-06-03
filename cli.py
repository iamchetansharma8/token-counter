import asyncio
import sys

from dotenv import load_dotenv

from counter import TokenCounter
from logging_config import log, setup_logging


def main():
    setup_logging()
    load_dotenv()
    script_name = sys.argv[0]
    log.info('Started CLI Tool Execution', script_name = script_name)
    if(len(sys.argv)<2):
        log.warning('File path not provided, terminating CLI tool')
    file_path = sys.argv[1]

    # if not Path(file_path).exists():
    #     log.error("File not found", file_path=file_path)
    #     print(f"Error: file not found: {file_path}", file=sys.stderr)
    #     sys.exit(1)

    try:
        log.info('Starting Execution', file_path=file_path)
        token_counter = TokenCounter()
        token_count_result = asyncio.run(token_counter.process_file(file_path))
        file_path_from_result = token_count_result.file_path
        file_size_bytes = token_count_result.file_size_bytes
        token_counts = token_count_result.token_counts
        cost_estimates = token_count_result.cost_estimates
        timestamp = token_count_result.timestamp

        log.info("File execution completed", file_path=file_path_from_result, file_size_bytes=file_size_bytes,
                 token_counts=token_counts, cost_estimates=cost_estimates, timestamp=timestamp)
    except Exception as e:
        log.exception('Exception raised during file processing', exception=e)
        raise


if __name__=="__main__":
    main()

# class TokenCountResult(BaseModel):
#     file_path: str
#     file_size_bytes: str
#     token_counts: list[TokenCount]
#     cost_estimates: list[CostEstimate]
#     timestamp: datetime
