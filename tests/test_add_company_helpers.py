import add_company


def test_get_repo_from_url_strips_host_and_trailing_slash():
    assert (
        add_company.get_repo_from_url("https://github.com/example/project/")
        == "example/project"
    )


def test_create_alternatives_md_trims_values_and_ignores_unpaired_items():
    rendered = add_company.create_alternatives_md(
        [" Notion ", " Coda ", "Unused"],
        [" https://notion.so ", " https://coda.io "],
    )

    assert rendered == "[Notion](https://notion.so), [Coda](https://coda.io)"


def test_create_new_line_formats_trimmed_company_row():
    line = add_company.create_new_line(
        " Analytics ",
        " Metabase ",
        " BI dashboards ",
        " https://metabase.com ",
        "https://github.com/metabase/metabase",
        [" Tableau "],
        [" https://tableau.com "],
    )

    assert line == (
        "Analytics|[Metabase](https://metabase.com)|BI dashboards|"
        '<a href=https://github.com/metabase/metabase><img '
        'src="https://img.shields.io/github/stars/metabase/metabase?style=social" '
        'width=150/></a>|[Tableau](https://tableau.com)|\n'
    )


def test_add_new_company_inserts_row_in_sorted_position(tmp_path, monkeypatch, capsys):
    readme = tmp_path / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# List",
                "|Category|Company|Description|GitHub Stars|Alternative to|",
                "|:-------|:------|:----------|:----------:|:------------:|",
                "Analytics|[Alpha](https://alpha.example)|First|<a href=https://github.com/example/alpha><img src=\"https://img.shields.io/github/stars/example/alpha?style=social\" width=150/></a>|[Sheet](https://sheet.example)|",
                "Billing|[Gamma](https://gamma.example)|Third|<a href=https://github.com/example/gamma><img src=\"https://img.shields.io/github/stars/example/gamma?style=social\" width=150/></a>|[Stripe](https://stripe.com)|",
                "",
                "<!-- END STARTUP LIST -->",
                "footer",
            ]
        )
        + "\n"
    )
    monkeypatch.chdir(tmp_path)

    result = add_company.add_new_company(
        "Analytics",
        "Beta",
        "Second",
        "https://beta.example",
        "https://github.com/example/beta",
        ["Sheet"],
        ["https://sheet.example"],
    )

    assert result == "ok, added!"
    capsys.readouterr()
    lines = readme.read_text().splitlines()
    beta_index = next(i for i, line in enumerate(lines) if "[Beta]" in line)
    gamma_index = next(i for i, line in enumerate(lines) if "[Gamma]" in line)
    assert beta_index < gamma_index


def test_add_new_company_returns_duplicate_without_rewriting(tmp_path, monkeypatch):
    readme = tmp_path / "README.md"
    original = (
        "# List\n"
        "|Category|Company|Description|GitHub Stars|Alternative to|\n"
        "|:-------|:------|:----------|:----------:|:------------:|\n"
        "Analytics|[Alpha](https://alpha.example)|First|<a href=https://github.com/example/alpha><img src=\"https://img.shields.io/github/stars/example/alpha?style=social\" width=150/></a>|[Sheet](https://sheet.example)|\n"
        "\n"
        "<!-- END STARTUP LIST -->\n"
    )
    readme.write_text(original)
    monkeypatch.chdir(tmp_path)

    result = add_company.add_new_company(
        "Analytics",
        "Alpha",
        "Changed",
        "https://changed.example",
        "https://github.com/example/changed",
        ["Changed"],
        ["https://changed.example"],
    )

    assert result == "This entry already exists"
    assert readme.read_text() == original
