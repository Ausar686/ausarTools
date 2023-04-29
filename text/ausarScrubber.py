# Made by Ausar686
# Last edited: 2023-04-29
# Last edited by: Ausar686
# Comment: Initial commit


from typing import Optional, Iterable
import os
import re
import time


class AusarScrubber:
    """
    Class for scrubbing data from raw PMC articles.
    To initialize an instance of the class simply type:
        scrubber = AusarScrubber()
    __init__ method takes no arguments.
    To perform scrubbing of a single file with a class entity simply type:
        scrubber(path)
    For further information check docs for __call__ method:
        doc(scrubber.__call__)
    """
    
    def __init__(self):
        """
        Initializes an instance of AusarScrubber object.
        """
        # Set the default value of output folder for preprocessing.
        self._output_folder = 'preprocessed'
        # Set the separator for PMC articles.
        self._separator = '===='
        # Set the stopstrings for 'front' part of PMC articles.
        self._stopstrings_front = [
            'cited',
            'license',
            'credited',
            'lawful purpose',
        ]
        # Set the stopstrings for 'body' part of PMC articles.
        self._stopstrings_body = [
            'acknowledgements',
            'supporting information',
        ]
    
    def cut_head(self, text: str, stopstrings: Iterable[str]) -> str:
        """
        Removes metadata from the beginning of the PMC article 
        according to the list of not-allowed strings.
        Args:
            text: A string to perform metadata removal at.
            stopstrings: An iterable with not-allowed strings to cut.
        Returns:
            preprocessed_text: 'text' without metadata.
        """
        # Find the last index of metadata.
        start_idx = max([text.lower().rfind(string) + len(string)*(text.lower().rfind(string)!=-1)
                         for string in stopstrings])
        # Metadata can end on '\n' or '.'. Remove this characters if required.
        if start_idx > 0:
            if not text[start_idx+1].isalpha():
                if not len(text) >= start_idx + 2 and text[start_idx+2].isalpha():
                    start_idx += 2
                else:
                    start_idx += 1
        preprocessed_text = text[min(len(text), max(start_idx, 0)):]
        return preprocessed_text
    
    def cut_tail(self, text: str, stopstrings: Iterable[str]) -> str:
        """
        Removes metadata from the end of the PMC article 
        according to the list of not-allowed strings.
        Args:
            text: A string to perform metadata removal at.
            stopstrings: An iterable with not-allowed strings to cut.
        Returns:
            preprocessed_text: 'text' without metadata.
        """
        # Find the first index of metadata.
        end_idx = min([text.lower().find(string) + (len(text)+1)*(text.lower().find(string)==-1)
                         for string in stopstrings])
        preprocessed_text = text[:end_idx]
        return preprocessed_text
    
    def remove_citing(self, text: str) -> str:
        """
        Removes cites from provided PMC article.
        Args:
            text: A string to remove cites from.
        Returns:
            preprocessed_text: 'text' without cites.
        """
        processed_text = re.sub(r'\[\d+\]|\(\d+\)', ' ', text)
        return processed_text
    
    def remove_refs(self, text: str) -> str:
        """
        Removes references from provided PMC article.
        Args:
            text: A string to remove references from.
        Returns:
            preprocessed_text: 'text' without references.
        """
        processed_text = re.sub(r'\(.*[,]\s*\d{4}.*\)', ' ', text)
        return processed_text
    
    def normalize(self, text: str) -> str:
        """
        Performs normalization of provided PMC article.
        Includes cites/references/unnecessary symbols removal,
        end-of-statement symbols convertion to periods and
        removing extra spaces.
        Args:
            text: A string to perform normaliztion at.
        Returns:
            preprocessed_text: Normalized 'text'.
        """
        # Remove citing from text.
        processed_text = self.remove_citing(text)
        # Remove references from text.
        processed_text = self.remove_refs(processed_text)
        # Remove all unnecessary symbols.
        processed_text = re.sub('[^a-zA-Z0-9!?,.\-\n]', ' ', processed_text)
        # Convert all end-of-statement symbols to periods, separated by spaces.
        processed_text = re.sub('[!?.]+', '.', processed_text)
        # Remove all extra spaces.
        processed_text = re.sub(' {2,}', ' ', processed_text)
        return processed_text
    
    def preprocess(self, text: str, mode: str) -> str:
        """
        Performs preprocessing for 'front' and 'body' parts of PMC article.
        Removes front/tail metadata and then performs text normalization.
        For further information check out AusarScrubber.normalize
        Args:
            text: A string to peform preprocessing at.
            mode: Preprocessing mode. Should be either 'front' or 'body'.
        Returns:
            preprocessed_text: Preprocessed text.
        """
        # Check whether 'mode' is correct or not.
        assert mode in ['front', 'body']
        if mode == 'front':
            # Remove metadata from front.
            processed_text = self.cut_head(text, self._stopstrings_front)
        elif mode == 'body':
            # Remove metadata from body.
            processed_text = self.cut_tail(text, self._stopstrings_body)
        # Normalize the text.
        processed_text = self.normalize(processed_text)
        return processed_text
    
    def __call__(self, path: str, output_dir: Optional[str] = None) -> None:
        """
        Performs scrub of the text file from PMC. 
        'front' and 'body' are preprocessed separately, but saved altogether. 
        'refs' part completely is removed completely during the preprocessing.
        Args:
            path: Path to the file to scrub.
            output_dir: Path to directory, where the output files should be stored.
                Note, that this directory will be created (if it doesn't exist).
        """
        # Check if the output_dir is not set.
        if output_dir is None:
            # Set the default value of output directory.
            output_dir = os.path.join(os.sep.join(path.split(os.sep)[:-2]), self._output_folder)
        # Check if output directory exists.
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        # Read the file.
        with open(path, 'r', encoding='utf-8') as file:
            text = file.read()
        # Assume, that article has the separated 'front'/'body' structure.
        try:
            # Get the raw 'front' and 'body' data.
            front, body = text.split(self._separator)[1:3]
        except Exception:
            # Set 'front' empty.
            front = ''
            # Set 'body' equal to the entire text of the article.
            body = text
        # Preprocess 'front'.
        preprocessed_front = self.preprocess(front, mode='front')
        # Preprocess 'body'.
        preprocessed_body = self.preprocess(body, mode='body')
        # Form the preprocessed text by merging 'front' and 'body' parts.
        preprocessed_text = preprocessed_front + '\n' + preprocessed_body
        # Get the filename.
        filename = path.split(os.sep)[-1]
        # Form path to the output file.
        output_path = os.path.join(output_dir, filename)
        # Write the preprocessed text into the output file.
        with open(output_path, 'w') as file:
            file.write(preprocessed_text)

    
    def scrub_pmc(self, pmc_folder: str) -> None:
        """
        Performs scrubbing from all articles in subfolders inside the provided folder.
        For further information check out __call__ method.
        Args:
            pmc_folder: Path to PMC folder with subfolders, which contain PMC articles.
        """
        # Initialize the counters for successfully/unsuccessfully scrubbed articles.
        nScrubbed = 0
        nFailed = 0
        # Get starting time.
        time_start = time.time()
        # Get all the paths to PMC subfolders.
        folders = [os.path.join(pmc_folder, folder) 
                   for folder in os.listdir(pmc_folder)]
        # Set the suffix for output directory path.
        suffix = f'{pmc_folder.split(os.sep)[-1]}_{self._output_folder}'
        # Set the 'output_path' parameter for __call__ method.
        # The output folder and PMC folder will be in the same directory.
        output_path = os.path.join(os.sep.join(pmc_folder.split(os.sep)[:-1]), suffix)
        # Display logging message.
        print('============ SCRUBBING LOG ============')
        # Iterate over PMC subfolders.
        for folder in folders:
            # Display the logging message.
            print(f'[INFO]: Started scrubbing the following directory: {folder}')
            # Iterate over articles in subfolder.
            for filename in os.listdir(folder):
                # Form a path to the article.
                path = os.path.join(folder, filename)
                # Check if it's a valid article (a file).
                if os.path.isfile(path):
                    try:
                        self.__call__(path, output_path)
                        print(f'[SUCCESS]: Successfully scrubbed {path}.')
                        nScrubbed += 1
                    except Exception as e:
                        print(f'[ERROR]: Failed to scrub {path} due to the following exception: {e}.')
                        nFailed += 1
        # Get ending time.
        time_end = time.time()
        # Get the execution time.
        execution_time = time_end - time_start
        # Convert execution time to visualization.
        hours = int(execution_time // 3600)
        mins = int((execution_time - 3600*hours) // 60)
        secs = round(execution_time - 3600*hours - 60*mins, 3)
        if hours < 10:
            hours = f'0{hours}'
        if mins < 10:
            mins = f'0{mins}'
        if secs < 10:
            secs = f'0{secs}'
        # Display logging summary.
        print('============ END OF LOG ============')
        print('[INFO]: Scrubbing completed.')
        print(f'[INFO]: Successfully scrubbed {nScrubbed} articles.')
        print(f'[INFO]: Failed to scrub {nFailed} articles.')
        print(f'[INFO]: Execution time: {hours}:{mins}:{secs}.')
