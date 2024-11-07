import time
from random import randint
from threading import Lock, Timer

MAX_BUCKET_SIZE = 5
DEFAULT_REFILL_RATE = 2
DEFAULT_REFILL_INTERVAL = 5


class RateLimiter:
    buckets = 0

    def __init__(
            self,
            max_tokens=MAX_BUCKET_SIZE,
            rate=DEFAULT_REFILL_RATE,
            interval=DEFAULT_REFILL_INTERVAL,
            token="__TOKEN__",
            token_generator=None
    ):
        """
        Inits the rate-limiter bucket. Starts a Timer to refill the bucket.
        :param max_tokens: The maximum number of tokens in the bucket.
        :param rate: The number of tokens created in each interval.
        :param interval: The interval in which tokens are generated.
        :param token: Define the shape of the generated token. Defaults to __TOKEN__
        :param token_generator: Use this to generate individual tokens. Function must return a str.
        """
        print(
            f"Rate-limiter bucket with a max-size of {max_tokens} Tokens created. \n"
            f"Token-creation happens at a rate of {rate} tokens every {interval}s. \n"
            f"----- Starting Logs -----")

        self.__lock = Lock()
        self.__max_tokens = max_tokens
        self.__rate = rate
        self.__interval = interval
        self.__token = token
        self.__token_generator = token_generator
        self.__bucket = [token] * max_tokens
        RateLimiter.buckets += 1
        self.__init_bucket()

    # Private methods

    def __init_bucket(self) -> None:
        """
        Starts the refill of the bucket based on the rate and the interval.
        """
        self.__set_interval(self.__add_token, self.__interval)

    def __set_interval(self, func, sec) -> Timer:
        """
        Calls given function in an interval.
        :param func: Function to be called.
        :param sec: Interval in seconds.
        :return: The timer, since it works recursively.
        """

        def func_wrapper():
            self.__set_interval(func, sec)
            func()

        t = Timer(sec, func_wrapper)
        t.start()
        return t

    def __add_token(self) -> None:
        """
        Adds Tokens based on the defined rate to the bucket. Locks the used bucket resource.
        """
        with self.__lock:
            # Add Tokens to instance variable.
            self.__add_tokens_to_local_variable_bucket(
                # Generate new tokens.
                self.__generate_tokens()
            )

            # TODO: No generic solution, works just with instance variables.
            if len(self.__bucket) > self.__max_tokens:
                self.__bucket = self.__bucket[:self.__max_tokens]

            print(f"{"-" * 5} Bucket filled to {len(self.__bucket)} tokens {"-" * 5}")

    def __add_tokens_to_local_variable_bucket(self, new_tokens) -> None:
        """
        Updates the bucket locally. Can be replaced to use a database or file-system instead.
        :param new_tokens: The new tokens to be added.
        """
        self.__bucket = self.__bucket + new_tokens

    def __generate_tokens(self) -> list:
        """
        Generate individual tokens by passing a generator function with the
        initialization of the rate limiter.
        :return: The list of tokens to be added.
        """
        # Use provided token generator
        if self.__token_generator:
            return list(map(self.__token_generator(), range(self.__rate)))

        # Use static token
        return [self.__token] * self.__rate

    # Public API

    def request_token(self, request_tokens=1) -> list | None:
        """
        Public API: Checks whether the bucket has available tokens and returns the requested amounts.
        Locks the resource while running.
        :param request_tokens: The number of tokens required for the request.
        Heavy computations can use up more tokens.
        :return: The requested token or None.
        """
        with self.__lock:
            if len(self.__bucket) >= request_tokens:
                # Using Fifo for taking out tokens.
                tokens = self.__bucket[:request_tokens]
                self.__bucket = self.__bucket[request_tokens:]

                print(f"SUCCESS: {len(tokens)} tokens granted")
                return tokens
            print("FAILED: Rate-limit reached.")
            return None

    def available_tokens(self):
        """
        Prints the number of available tokens in the bucket.
        """
        with self.__lock:
            return len(self.__bucket)


def main():
    bucket = RateLimiter()

    while True:
        time_till_next_request = randint(1, 10) / 10 * 4
        time.sleep(time_till_next_request)

        number_of_tokens = randint(1, 3)
        bucket.request_token(request_tokens=number_of_tokens)

        print(f" ({bucket.available_tokens()} left)")


if __name__ == "__main__":
    main()
