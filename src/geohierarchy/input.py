from geohierarchy.io.opener_registry import OpenerRegistry

class HierInput:
    def __init__(
                self,
                filepath: str,
                column: str = None,
                value: int | float = None,
                z: int | float = None,
                layer: int = None,
                mask: str = None,
                global_mask: str = None,
                clip: str = None,
                global_clip: str = None,
                opener_kwargs: dict = None,
                ):
        #TODO: check all valid inputs
        self.filepath = filepath
        self.column = column
        self.value = value
        self.z = z
        self.layer = layer
        self.mask = mask
        self.global_mask = global_mask
        self.clip = clip
        self.global_clip = global_clip
        self.opener_kwargs = opener_kwargs

    def open(self):
        print('accessing open')
        opener = OpenerRegistry.get(self.filepath)
        data = opener(self.filepath, **self.opener_kwargs)

        pass