from pydantic import BaseModel, Field, HttpUrl


class ContentSection(BaseModel):
    heading: str | None = None
    content: list[str] = Field(
        default_factory=list
    )


class WebPage(BaseModel):
    url: str
    title: str | None = None

    sections: list[ContentSection] = Field(
        default_factory=list
    )

    def to_structured_text(
        self,
        max_chars: int = 18_000,
    ) -> str:
        output: list[str] = []

        output.append("SOURCE")
        output.append(f"URL: {self.url}")

        if self.title:
            output.append(
                f"TITLE: {self.title}"
            )

        output.append("")

        current_length = sum(
            len(line) + 1
            for line in output
        )

        for section in self.sections:

            header = (
                f"## {section.heading}\n"
                if section.heading
                else ""
            )

            remaining = (
                max_chars - current_length
            )

            if remaining <= 0:
                break

            if len(header) > remaining:
                break

            output.append(header)
            current_length += len(header)

            for line in section.content:

                line_length = len(line) + 1

                if (
                    current_length
                    + line_length
                    > max_chars
                ):
                    return "\n".join(
                        output
                    ).strip()

                output.append(line)
                current_length += line_length

            output.append("")

        return "\n".join(
            output
        ).strip()


class StructuredProduct(BaseModel):



    def to_embedding_text(self) -> str:
        """
        Create a compact semantic representation of the product
        for embedding generation.

        Only include fields that actually contain information.
        """

        parts: list[str] = []

        if self.product_name:
            parts.append(
                f"product: {self.product_name}"
            )

        if self.brand:
            parts.append(
                f"brand: {self.brand}"
            )

        if self.category:
            parts.append(
                f"category: {self.category}"
            )

        if self.product_id:
            parts.append(
                f"product_id: {self.product_id}"
            )

        if self.price:
            if self.currency:
                parts.append(
                    f"price: {self.currency} {self.price}"
                )
            else:
                parts.append(
                    f"price: {self.price}"
                )

        if self.color:
            parts.append(
                f"color: {self.color}"
            )

        if self.sizes:
            parts.append(
                f"sizes: {', '.join(self.sizes)}"
            )

        if self.availability:
            parts.append(
                f"availability: {self.availability}"
            )

        if self.description:
            parts.append(
                f"description: {self.description}"
            )

        if self.features:
            parts.append(
                "features: "
                + " | ".join(self.features)
            )

        if self.material:
            parts.append(
                f"material: {self.material}"
            )

        if self.care_instructions:
            parts.append(
                f"care: {self.care_instructions}"
            )

        if self.rating is not None:
            parts.append(
                f"rating: {self.rating}"
            )

        if self.review_count:
            parts.append(
                f"review_count: {self.review_count}"
            )

        if self.shipping:
            parts.append(
                f"shipping: {self.shipping}"
            )

        if self.returns:
            parts.append(
                f"returns: {self.returns}"
            )

        if self.country_of_origin:
            parts.append(
                f"country_of_origin: "
                f"{self.country_of_origin}"
            )

        if self.manufacturer:
            parts.append(
                f"manufacturer: {self.manufacturer}"
            )

        return "\n".join(parts)
    source_site: str | None = Field(
        default=None,
        description=(
            "Website or retailer explicitly identified "
            "in the source. Do not infer from domain alone."
        ),
    )

    product_name: str | None = Field(
        default=None,
        description="Exact product name from the source.",
    )

    brand: str | None = Field(
        default=None,
        description=(
            "Product brand only when explicitly identified. "
            "Do not infer from product name, collection, "
            "technology, retailer, or manufacturer."
        ),
    )

    category: str | None = None
    product_id: str | None = None

    price: str | None = None
    currency: str | None = None

    color: str | None = None
    sizes: list[str] = Field(
        default_factory=list
    )

    availability: str | None = None

    description: str | None = None
    features: list[str] = Field(
        default_factory=list
    )

    material: str | None = None
    care_instructions: str | None = None

    rating: float | None = None
    review_count: str | None = None

    shipping: str | None = None
    returns: str | None = None

    country_of_origin: str | None = None
    manufacturer: str | None = None

    url: str | None = None


class ExtractRequest(BaseModel):
    url: HttpUrl


class ExtractResponse(BaseModel):
    url: str
    raw_file: str
    structured_file: str
    raw_characters: int
    structured_characters: int
    content: str


class ProductExtractResponse(BaseModel):
    url: str
    product: StructuredProduct

class EmbeddingRecord(BaseModel):
    """
    Local representation of an embedded document.

    This is deliberately storage-agnostic so that the same object
    can later be written to Supabase/pgvector.
    """

    source_url: str

    product_id: str | None = None

    content: str

    model: str

    dimensions: int

    embedding: list[float] = Field(
        default_factory=list
    )

class EmbedProductResponse(BaseModel):
    url: str
    product_id: str | None
    supabase_id: int
    model: str
    dimensions: int


def to_embedding_text(
    self,
) -> str:
    parts: list[str] = []

    if self.product_name:
        parts.append(
            f"product: {self.product_name}"
        )

    if self.brand:
        parts.append(
            f"brand: {self.brand}"
        )

    if self.category:
        parts.append(
            f"category: {self.category}"
        )

    if self.product_id:
        parts.append(
            f"product_id: {self.product_id}"
        )

    if self.price:
        price = self.price

        if self.currency:
            price = (
                f"{self.currency} {price}"
            )

        parts.append(
            f"price: {price}"
        )

    if self.color:
        parts.append(
            f"color: {self.color}"
        )

    if self.sizes:
        parts.append(
            f"sizes: "
            f"{', '.join(self.sizes)}"
        )

    if self.availability:
        parts.append(
            f"availability: "
            f"{self.availability}"
        )

    if self.description:
        parts.append(
            f"description: "
            f"{self.description}"
        )

    if self.features:
        parts.append(
            "features: "
            + " | ".join(self.features)
        )

    if self.material:
        parts.append(
            f"material: {self.material}"
        )

    if self.care_instructions:
        parts.append(
            f"care: "
            f"{self.care_instructions}"
        )

    if self.rating is not None:
        parts.append(
            f"rating: {self.rating}"
        )

    if self.review_count:
        parts.append(
            f"reviews: "
            f"{self.review_count}"
        )

    if self.shipping:
        parts.append(
            f"shipping: {self.shipping}"
        )

    if self.returns:
        parts.append(
            f"returns: {self.returns}"
        )

    return "\n".join(parts)



class MerchantIngestResponse(BaseModel):
    id: int
    url: str
    product: StructuredProduct
    model: str
    dimensions: int