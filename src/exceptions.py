class KnowledgeBaseError(Exception):
    pass


class ValidationError(KnowledgeBaseError):
    pass


class ItemNotFoundError(KnowledgeBaseError):
    pass


class StorageError(KnowledgeBaseError):
    pass


class DataCorruptionError(StorageError):
    pass


class ImportExportError(KnowledgeBaseError):
    pass