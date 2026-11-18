"""Two common misconceptions in each of the original Pandas exercises."""


def add_wrong_answers(catalog):
    def change(key, before, after):
        original = catalog[key]["pandas"]
        if before not in original:
            raise ValueError(f"Unknown reference expression in Database #{key}: {before}")
        return original.replace(before, after)

    answers = {
        175: [change(175, "how='left'", "how='inner'"), change(175, "merge(Address,", "merge(Address.drop_duplicates('personId'),")],
        176: [change(176, ".drop_duplicates()", ""), change(176, "values[1]", "values[0]")],
        177: [change(177, ".drop_duplicates()", ""), change(177, "ascending=False", "ascending=True")],
        178: [change(178, "method='dense'", "method='min'"), change(178, "sort_values('score', ascending=False)", "sort_values('score')")],
        181: [change(181, "salary_e >", "salary_e >="), change(181, "salary_e >", "salary_e <")],
        182: [change(182, "Person.email.duplicated(keep=False)", "~Person.email.duplicated()"),
              change(182, ".drop_duplicates()", "")],
        183: [change(183, "~Customers.id", "Customers.id"), change(183, "Orders.customerId", "Orders.id")],
        196: [change(196, "Person.drop_duplicates('email', inplace=True)", "Person.drop_duplicates('email', keep='last', inplace=True)"),
              "Person.drop(Person.index[Person.id > 1], inplace=True)"],
        197: [change(197, "temperature >", "temperature >="),
              "rows = Weather.sort_values('recordDate')\nreturn rows.loc[rows.temperature.diff().gt(0), ['id']]"],
        584: [change(584, ".fillna(True)", ".fillna(False)"), "return Customer.loc[Customer.referee_id.isna(), ['name']]"],
        595: [change(595, ") | (", ") & ("), change(595, ">=", ">")],
        620: [change(620, " & Cinema.description.ne('boring')", ""), change(620, "ascending=False", "ascending=True")],
        1050: [change(1050, ">= 3", "> 3"), change(1050, ">= 3", ">= 2")],
        1683: [change(1683, "> 15", ">= 15"), change(1683, "> 15", "< 15")],
        1729: [change(1729, "sort=True", "sort=True").replace(".reset_index(", ".sort_index(ascending=False).reset_index("),
               change(1729, "groupby('user_id'", "groupby('follower_id'").replace(".reset_index(name='followers_count')", ".reset_index(name='followers_count').rename(columns={'follower_id':'user_id'})")],
        1757: [change(1757, ") & (", ") | ("), "return Products.loc[Products.recyclable.eq('Y'), ['product_id']]"],
        1789: [change(1789, "count.eq(1) | ", ""), change(1789, "primary_flag.eq('Y')", "primary_flag.eq('N')")],
        1873: [change(1873, " & ~result.name.str.startswith('M')", ""), change(1873, "result.employee_id.mod(2).eq(1) & ", "")],
        2252: [change(2252, ".reset_index()", ".fillna(0).reset_index()"),
               change(2252, ".sort_index(axis=1)", ".sort_index(axis=1, ascending=False)")],
    }
    for key, variants in answers.items():
        catalog[key]["wrong_pandas"] = variants
