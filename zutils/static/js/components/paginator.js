/*
Require:
  <script src="https://cdnjs.cloudflare.com/ajax/libs/URI.js/1.18.10/URI.min.js"></script>
Usage:
 <Pagination count=32
 per_page=25
 current_page=1
 subpagenums="2"
 />
 */
class Pagination extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            count: props.count,
            per_page: props.per_page,
            current_page: props.current_page,
            subpagenums: props.subpagenums || 3

        }
    }

    render() {
        /*

         count(int): , - total items
         num_pages(int):  , - total pages
         per_page(int): , - item per page
         object_list(array): , - items,
         current_page(int): , - current page
         */
        let count = this.state.count;
        let per_page = this.state.per_page;
        let current_page = this.state.current_page;
        let subpagenums = this.state.subpagenums;


        let num_pages = Math.ceil(count / per_page);


        if (num_pages <= 1) {
            return <div></div>
        }

        let page_start = 1;
        let page_end = num_pages;
        subpagenums = Math.min(num_pages - 1, subpagenums);
        let start = Math.max(page_start, current_page - subpagenums);
        let end = Math.min(page_end, current_page + subpagenums);
        let page_items = _.range(start, end + 1);
        let index = page_items.indexOf(page_start);
        if (index == -1) {
            page_items.unshift(1)
        }
        index = page_items.indexOf(page_end);
        if (index == -1) {
            page_items.push(page_end)
        }
        let current_href = window.location.href;


        return <nav aria-label="Page navigation">
            <ul className="pagination">
                {page_items.map(n => {
                    let url = new URI(current_href);
                    return <li><a href={"?" + url.addQuery('page', n).query()}>{n}</a></li>
                })}
            </ul>
        </nav>
    }

}